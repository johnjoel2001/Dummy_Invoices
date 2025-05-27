
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from fuzzywuzzy import fuzz

from db import (
    init_db,
    add_order,
    get_all_companies,
    get_pending_orders_with_items,
    delete_order_by_serial,
    apply_payment,
    apply_partial_to_invoice,
    get_total_quantity,
    add_shipping_fee,
    find_orders_with_shipping,
    remove_shipping_fee_by_order,
    find_unpaid_orders_by_company,
    delete_order_by_id,
    get_all_orders_with_items,
)

from gpt_parser import extract_order_info, extract_payment_info

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
init_db()

user_payment_context = {}
user_shipping_context = {}
user_shipping_removal_context = {}

def fuzzy_match_company(input_name):
    all_companies = get_all_companies()
    best_match = None
    best_score = 0
    for name in all_companies:
        score = fuzz.partial_ratio(input_name.lower(), name.lower())
        if score > best_score:
            best_score = score
            best_match = name
    return best_match

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id

    # Delete invoice (case-insensitive)
    if text.lower().startswith("delete invoice"):
        try:
            serial = int(text.lower().split("delete invoice")[1].strip())
            success = delete_order_by_serial(serial)
            if success:
                await update.message.reply_text(f"🗑️ Invoice {serial} deleted successfully.")
            else:
                await update.message.reply_text("❌ Invalid invoice number.")
        except:
            await update.message.reply_text("❌ Usage: delete invoice 2")
        return

    # Invoice selection for payment
    if user_id in user_payment_context and text.lower().startswith("invoice"):
        try:
            selected = int(text.lower().split("invoice")[1].strip()) - 1
            info = user_payment_context[user_id]
            invoice = info["invoices"][selected]
            order_id = invoice[0]
            amount = info["amount"]

            result = apply_partial_to_invoice(order_id, amount)
            await update.message.reply_text(result)
            del user_payment_context[user_id]
        except:
            await update.message.reply_text("❌ Invalid invoice number.")
        return

    # Shipping charges confirmation
    if user_id in user_shipping_context:
        order_id = user_shipping_context[user_id]["order_id"]
        total_qty = user_shipping_context[user_id]["total_qty"]
        if text.lower() == "yes":
            shipping = 50 if total_qty <= 1000 else 100
            new_total = add_shipping_fee(order_id, shipping)
            await update.message.reply_text(f"🚚 Shipping fee ₹{shipping} added.\nNew total: ₹{new_total}")
        elif text.lower() == "no":
            await update.message.reply_text("✅ No shipping fee added.")
        else:
            await update.message.reply_text("❌ Please reply with 'yes' or 'no'.")
            return
        del user_shipping_context[user_id]
        return

    # Delete shipping fee
    if text.lower().startswith("delete shipping fee for"):
        name = text.lower().split("delete shipping fee for")[1].strip()
        company = fuzzy_match_company(name)
        if not company:
            await update.message.reply_text("❌ Customer not found.")
            return
        results = find_orders_with_shipping(company)
        if not results:
            await update.message.reply_text("⚠️ No invoices with shipping fee found for this customer.")
            return
        if len(results) == 1:
            order_id = results[0][0]
            new_total = remove_shipping_fee_by_order(order_id)
            await update.message.reply_text(f"🚫 Shipping fee removed from invoice #{order_id}. New total: ₹{new_total}")
        else:
            user_shipping_removal_context[user_id] = {
                "company": company,
                "candidates": results
            }
            reply = f"🧾 Multiple invoices found for {company.title()}:\n"
            for i, (oid, amt, total) in enumerate(results, 1):
                reply += f"{i}) Invoice #{oid} — Total: ₹{amt}, Items: ₹{round(total, 2)}\n"
            reply += "\nReply with `remove invoice <number>` to remove shipping fee."
            await update.message.reply_text(reply)
        return

    if user_id in user_shipping_removal_context and text.lower().startswith("remove invoice"):
        try:
            idx = int(text.lower().split("remove invoice")[1].strip()) - 1
            context_data = user_shipping_removal_context[user_id]
            order_id = context_data["candidates"][idx][0]
            new_total = remove_shipping_fee_by_order(order_id)
            await update.message.reply_text(f"🚫 Shipping fee removed from invoice #{order_id}. New total: ₹{new_total}")
            del user_shipping_removal_context[user_id]
        except:
            await update.message.reply_text("❌ Invalid invoice number.")
        return

    # Handle order
    if "ordered" in text.lower():
        data = extract_order_info(text)
        if data and "company" in data and "orders" in data:
            amount, order_id, total_qty = add_order(data["company"], data["orders"])
            order_lines = "\n".join(
                [f"{o['description'].title()} - {o['quantity']} pairs @ ₹{o['rate']} = ₹{round(o['quantity'] * o['rate'], 2)}"
                 for o in data["orders"]]
            )
            await update.message.reply_text(
                f"✅ Order saved for {data['company'].title()}:\n{order_lines}\n\nTotal = ₹{amount}"
            )
            user_shipping_context[user_id] = {
                "order_id": order_id,
                "total_qty": total_qty
            }
            await update.message.reply_text("Do you want to add shipping charges? (yes/no)")
        else:
            await update.message.reply_text("❌ Couldn't understand the order message.")
        return

    # Handle payment
    if "paid" in text.lower():
        data = extract_payment_info(text)
        if data:
            company = fuzzy_match_company(data["company"])
            if not company:
                await update.message.reply_text("❌ Customer not found.")
                return

            result = apply_payment(company, data["amount"])
            if isinstance(result, str):
                await update.message.reply_text(result)
            elif isinstance(result, dict) and result.get("multiple"):
                user_payment_context[user_id] = result
                invoices = result["invoices"]
                reply = f"🔸 {company.title()} has multiple unpaid invoices:\n"
                for i, inv in enumerate(invoices, start=1):
                    order_id, paid, total = inv
                    reply += f"{i}) Invoice #{order_id}: Paid ₹{paid} / ₹{total}, Balance ₹{round(total - paid, 2)}\n"
                reply += "\nPlease reply with `invoice <number>` to apply the ₹{} payment.".format(data["amount"])
                await update.message.reply_text(reply)
        else:
            await update.message.reply_text("❌ Couldn't understand the payment message.")
        return

    # Fallback
    await update.message.reply_text("🤖 Please enter a valid order, payment, or command.")

async def invoices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = get_all_orders_with_items()
    if not orders:
        await update.message.reply_text("📦 No orders found.")
        return

    msg = "📋 *All Invoices:*\n\n"
    for idx, order in enumerate(orders, start=1):
        balance = round(order["amount"] - order["paid_amount"], 2)
        status = "✅ Paid" if balance == 0 else f"❌ Pending ₹{balance}"

        msg += (
            f"*{idx}) {order['company'].title()}*\n"
            f"🧾 Total: ₹{order['amount']} | Paid: ₹{order['paid_amount']} | {status}\n"
            f"📅 Order Date: {order['order_date']}\n"
        ) 
        # Show payment date only if any amount is paid
        if order["paid_amount"] > 0 and "payment_date" in order:
            payment_date = order["payment_date"].split(" ")[0]
            msg += f"💳 Payment Date: {payment_date}\n"

        for desc, qty, rate in order["items"]:
            line_total = round(qty * rate, 2)
            msg += f"• {desc.title()} — {qty} pairs @ ₹{rate} = ₹{line_total}\n"

        if order["shipping_fee"]:
            msg += f"🚚 Shipping Fee: ₹{order['shipping_fee']}\n"

        msg += "──────────────────────────────\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

async def pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = get_pending_orders_with_items()
    if not orders:
        await update.message.reply_text("🎉 All payments are cleared!")
        return

    msg = "📌 *Pending Payments:*\n\n"
    for idx, order in enumerate(orders, start=1):
        balance = round(order["amount"] - order["paid_amount"], 2)

        msg += (
            f"*{idx}) {order['company'].title()}*\n"
            f"🧾 Total: ₹{order['amount']} | Paid: ₹{order['paid_amount']} | Balance: ₹{balance}\n"
            f"📅 Order Date: {order['order_date']}\n"
        )

        for desc, qty, rate in order["items"]:
            line_total = round(qty * rate, 2)
            msg += f"• {desc.title()} — {qty} pairs @ ₹{rate} = ₹{line_total}\n"

        if order["shipping_fee"]:
            msg += f"🚚 Shipping Fee: ₹{order['shipping_fee']}\n"

        msg += "──────────────────────────────\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("pending", pending))
    app.add_handler(CommandHandler("invoices", invoices))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running...")
    app.run_polling()

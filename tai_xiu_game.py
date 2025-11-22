import telebot
from tai_xiu_game import TaiXiuGame
import re
import os
from datetime import datetime

# Cấu hình - THAY ĐỔI CÁC GIÁ TRỊ NÀY
BOT_TOKEN = "8245076544:AAECLsZHJqt_jun8ZVY7rqjCwxmMtPpmlC4"
CHAT_ID = "-5053871915"
ADMIN_USER_ID = "6611733744"

# Khởi tạo bot
bot = telebot.TeleBot(8245076544:AAECLsZHJqt_jun8ZVY7rqjCwxmMtPpmlC4)
game = TaiXiuGame(8245076544:AAECLsZHJqt_jun8ZVY7rqjCwxmMtPpmlC4, -5053871915)
game.admin_chat_id = 6611733744

# Biến tạm để lưu thông tin rút tiền
pending_withdraws = {}

def get_player_name(message):
    """Tạo tên người chơi từ thông tin Telegram"""
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    if not full_name:
        full_name = f"User_{message.from_user.id}"
    return f"{full_name}_{message.from_user.id}"

def get_admin_name(message):
    """Lấy tên admin"""
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    return f"{first_name} {last_name}".strip() or f"Admin_{message.from_user.id}"

def is_admin(message):
    """Kiểm tra có phải admin không"""
    return str(message.from_user.id) == 6611733744

def is_private_chat(message):
    """Kiểm tra có phải chat riêng không"""
    return message.chat.type == 'private'

def parse_amount(amount_text):
    """Phân tích số tiền từ text (hỗ trợ k, m)"""
    try:
        amount_text = amount_text.lower().strip()
        multiplier = 1
        
        if amount_text.endswith('k'):
            multiplier = 1000
            amount_text = amount_text[:-1]
        elif amount_text.endswith('m'):
            multiplier = 1000000
            amount_text = amount_text[:-1]
        elif amount_text.endswith('b'):
            multiplier = 1000000000
            amount_text = amount_text[:-1]
            
        amount_text = re.sub(r'[^\d.]', '', amount_text)
        
        if not amount_text:
            return 0
            
        amount = float(amount_text) * multiplier
        return int(amount)
    except (ValueError, TypeError):
        return 0

# ========== COMMAND CƠ BẢN ==========
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if is_private_chat(message) and is_admin(message):
        welcome_text = """
🎰 <b>GAME TÀI XỈU - CASINO ONLINE</b> 🎰

<b>Luật chơi:</b>
- Tổng 3 xí ngầu 11-17: TÀI 🎯
- Tổng 3 xí ngầu 4-10: XỈU 🎯
- Tỷ lệ trả thưởng: 1.95
- <b>Kết quả hoàn toàn ngẫu nhiên!</b>

<b>Lệnh chính:</b>
/naptien [số tiền] - Nạp tiền
/ruttien - Rút tiền
/bet [tai|xiu] [số tiền] - Đặt cược
/balance - Thống kê cá nhân
/thongke - Xem thống kê game
/xacsuat - Xem xác suất thực tế
/ls_rut - Lịch sử rút tiền
/bangxephang - Bảng xếp hạng
/lichsu - Lịch sử game

<b>Lệnh Admin (chỉ trong chat riêng):</b>
/ds_nguoichoi - DS tất cả người chơi
/ds_soi - DS người chơi đang soi
/bat_soi [tên] - Bật chế độ soi
/tat_soi [tên] - Tắt chế độ soi
/ds_rut - DS yêu cầu rút tiền
/duyet_rut [id] - Duyệt rút tiền
/tuchoi_rut [id] [lý do] - Từ chối rút tiền
/play - Xúc ngay
/dieuchinh_sodu [tên] [số tiền] - Điều chỉnh số dư
        """
    else:
        welcome_text = """
🎰 <b>GAME TÀI XỈU - CASINO ONLINE</b> 🎰

<b>Luật chơi:</b>
- Tổng 3 xí ngầu 11-17: TÀI 🎯
- Tổng 3 xí ngầu 4-10: XỈU 🎯
- Tỷ lệ trả thưởng: 1.95
- <b>Kết quả hoàn toàn ngẫu nhiên!</b>

<b>Lệnh chính:</b>
/naptien [số tiền] - Nạp tiền
/ruttien - Rút tiền
/bet [tai|xiu] [số tiền] - Đặt cược
/balance - Thống kê cá nhân
/thongke - Xem thống kê game
/xacsuat - Xem xác suất thực tế
/ls_rut - Lịch sử rút tiền
/bangxephang - Bảng xếp hạng
/lichsu - Lịch sử game

💡 <i>Chat riêng với bot để được hỗ trợ</i>
        """
    
    bot.reply_to(message, welcome_text, parse_mode='HTML')

@bot.message_handler(commands=['thongke', 'stats'])
def show_statistics(message):
    stats = game.get_game_statistics()
    bot.reply_to(message, stats, parse_mode='HTML')

@bot.message_handler(commands=['xacsuat', 'probability'])
def show_probability(message):
    probability_info = game.get_probability_info()
    bot.reply_to(message, probability_info, parse_mode='HTML')

@bot.message_handler(commands=['naptien'])
def deposit_money(message):
    try:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ Sai cú pháp! Dùng: /naptien [số tiền]\nVí dụ: /naptien 100000 hoặc /naptien 100k")
            return
            
        amount_text = command_parts[1]
        amount = parse_amount(amount_text)
        
        if amount <= 0:
            bot.reply_to(message, "❌ Số tiền nạp phải lớn hơn 0!")
            return
            
        player_name = get_player_name(message)
        success, result_msg = game.deposit_money(player_name, amount)
        bot.reply_to(message, result_msg, parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

@bot.message_handler(commands=['ruttien'])
def start_withdraw(message):
    player_name = get_player_name(message)
    balance = game.get_player_balance(player_name)
    
    if balance < 50000:
        bot.reply_to(message, f"❌ Số dư tối thiểu để rút là 50,000 VND!\n💰 Số dư hiện tại: {balance:,} VND", parse_mode='HTML')
        return
    
    pending_withdraws[player_name] = {'step': 'amount'}
    
    bot.reply_to(message, 
                 f"💰 <b>RÚT TIỀN</b>\n\n"
                 f"Số dư khả dụng: {balance:,} VND\n"
                 f"💰 <b>Bước 1:</b> Nhập số tiền muốn rút (tối thiểu 50,000 VND)\n"
                 f"Ví dụ: 100000 hoặc 100k", 
                 parse_mode='HTML')

@bot.message_handler(commands=['bet'])
def place_bet(message):
    try:
        command_parts = message.text.split()
        if len(command_parts) < 3:
            bot.reply_to(message, "❌ Sai cú pháp! Dùng: /bet [tai|xiu] [số tiền]\nVí dụ: /bet tai 100000 hoặc /bet xiu 50k")
            return
            
        bet_type = command_parts[1]
        amount_text = command_parts[2]
        amount = parse_amount(amount_text)
        
        if amount <= 0:
            bot.reply_to(message, "❌ Số tiền cược phải lớn hơn 0!")
            return
            
        player_name = get_player_name(message)
        success, result_msg = game.place_bet(player_name, bet_type, amount)
        bot.reply_to(message, result_msg, parse_mode='HTML')
        
        if success:
            balance = game.get_player_balance(player_name)
            bot.send_message(message.chat.id, f"💰 Số dư hiện tại: {balance:,} VND", parse_mode='HTML')
            
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

@bot.message_handler(commands=['balance', 'sodu'])
def check_balance(message):
    player_name = get_player_name(message)
    stats = game.get_player_stats(player_name)
    bot.reply_to(message, stats, parse_mode='HTML')

@bot.message_handler(commands=['bangxephang', 'top'])
def show_leaderboard(message):
    leaderboard = game.get_leaderboard(10)
    bot.reply_to(message, leaderboard, parse_mode='HTML')

@bot.message_handler(commands=['lichsu', 'history'])
def show_history(message):
    history = game.get_recent_games(5)
    bot.reply_to(message, history, parse_mode='HTML')

@bot.message_handler(commands=['ls_rut'])
def withdraw_history(message):
    player_name = get_player_name(message)
    history = game.get_player_withdraw_history(player_name)
    bot.reply_to(message, history, parse_mode='HTML')

# ========== COMMAND ADMIN ==========
@bot.message_handler(commands=['ds_nguoichoi'])
def list_all_players(message):
    if not is_admin(message) or not is_private_chat(message):
        bot.reply_to(message, "❌ Lệnh này chỉ khả dụng trong chat riêng với admin!")
        return
        
    players_info = game.get_all_players_info()
    if len(players_info) > 4000:
        parts = [players_info[i:i+4000] for i in range(0, len(players_info), 4000)]
        for part in parts:
            bot.reply_to(message, part, parse_mode='HTML')
    else:
        bot.reply_to(message, players_info, parse_mode='HTML')

@bot.message_handler(commands=['chitiet_nguoichoi'])
def player_detail(message):
    if not is_admin(message) or not is_private_chat(message):
        bot.reply_to(message, "❌ Lệnh này chỉ khả dụng trong chat riêng với admin!")
        return
        
    try:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ Sai cú pháp! Dùng: /chitiet_nguoichoi [tên_người_chơi]")
            return
            
        player_name = command_parts[1]
        detail = game.get_player_detail(player_name)
        bot.reply_to(message, detail, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

@bot.message_handler(commands=['reset_nguoichoi'])
def reset_player(message):
    if not is_admin(message) or not is_private_chat(message):
        bot.reply_to(message, "❌ Lệnh này chỉ khả dụng trong chat riêng với admin!")
        return
        
    try:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ Sai cú pháp! Dùng: /reset_nguoichoi [tên_người_chơi]")
            return
            
        player_name = command_parts[1]
        success, result_msg = game.reset_player_data(player_name)
        bot.reply_to(message, result_msg, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

@bot.message_handler(commands=['dieuchinh_sodu'])
def adjust_balance(message):
    if not is_admin(message) or not is_private_chat(message):
        bot.reply_to(message, "❌ Lệnh này chỉ khả dụng trong chat riêng với admin!")
        return
        
    try:
        command_parts = message.text.split()
        if len(command_parts) < 3:
            bot.reply_to(message, "❌ Sai cú pháp! Dùng: /dieuchinh_sodu [tên_người_chơi] [số_tiền]")
            return
            
        player_name = command_parts[1]
        amount_text = command_parts[2]
        amount = parse_amount(amount_text)
        
        success, result_msg = game.adjust_player_balance(player_name, amount)
        bot.reply_to(message, result_msg, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

@bot.message_handler(commands=['bat_soi'])
def enable_soi_mode(message):
    if not is_admin(message) or not is_private_chat(message):
        bot.reply_to(message, "❌ Lệnh này chỉ khả dụng trong chat riêng với admin!")
        return
        
    try:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ Sai cú pháp! Dùng: /bat_soi [tên_người_chơi]")
            return
            
        player_name = command_parts[1]
        success, result_msg = game.enable_soi_mode(player_name)
        bot.reply_to(message, result_msg, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

@bot.message_handler(commands=['tat_soi'])
def disable_soi_mode(message):
    if not is_admin(message) or not is_private_chat(message):
        bot.reply_to(message, "❌ Lệnh này chỉ khả dụng trong chat riêng với admin!")
        return
        
    try:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ Sai cú pháp! Dùng: /tat_soi [tên_người_chơi]")
            return
            
        player_name = command_parts[1]
        success, result_msg = game.disable_soi_mode(player_name)
        bot.reply_to(message, result_msg, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

@bot.message_handler(commands=['ds_soi'])
def list_soi_players(message):
    if not is_admin(message) or not is_private_chat(message):
        bot.reply_to(message, "❌ Lệnh này chỉ khả dụng trong chat riêng với admin!")
        return
        
    soi_list = game.get_soi_mode_players()
    bot.reply_to(message, soi_list, parse_mode='HTML')

@bot.message_handler(commands=['ds_rut'])
def list_pending_withdraws(message):
    if not is_admin(message) or not is_private_chat(message):
        bot.reply_to(message, "❌ Lệnh này chỉ khả dụng trong chat riêng với admin!")
        return
        
    pending_list = game.get_pending_withdraws()
    bot.reply_to(message, pending_list, parse_mode='HTML')

@bot.message_handler(commands=['duyet_rut'])
def approve_withdraw(message):
    if not is_admin(message) or not is_private_chat(message):
        bot.reply_to(message, "❌ Lệnh này chỉ khả dụng trong chat riêng với admin!")
        return
        
    try:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ Sai cú pháp! Dùng: /duyet_rut [mã_yêu_cầu]")
            return
            
        withdraw_id = int(command_parts[1])
        admin_name = get_admin_name(message)
        
        success, result_msg = game.approve_withdraw(withdraw_id, admin_name)
        bot.reply_to(message, result_msg, parse_mode='HTML')
        
    except (ValueError, IndexError):
        bot.reply_to(message, "❌ Sai cú pháp! Dùng: /duyet_rut [mã_yêu_cầu]")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

@bot.message_handler(commands=['tuchoi_rut'])
def reject_withdraw(message):
    if not is_admin(message) or not is_private_chat(message):
        bot.reply_to(message, "❌ Lệnh này chỉ khả dụng trong chat riêng với admin!")
        return
        
    try:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ Sai cú pháp! Dùng: /tuchoi_rut [mã_yêu_cầu] [lý do]")
            return
            
        withdraw_id = int(command_parts[1])
        reason = " ".join(command_parts[2:]) if len(command_parts) > 2 else "Không có lý do cụ thể"
        admin_name = get_admin_name(message)
        
        success, result_msg = game.reject_withdraw(withdraw_id, admin_name, reason)
        bot.reply_to(message, result_msg, parse_mode='HTML')
        
    except (ValueError, IndexError):
        bot.reply_to(message, "❌ Sai cú pháp! Dùng: /tuchoi_rut [mã_yêu_cầu] [lý do]")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

@bot.message_handler(commands=['play'])
def play_round(message):
    if not is_admin(message) or not is_private_chat(message):
        bot.reply_to(message, "❌ Lệnh này chỉ khả dụng trong chat riêng với admin!")
        return
        
    try:
        result = game.play_round()
        if game.chat_id:
            bot.send_message(game.chat_id, result, parse_mode='HTML')
        bot.reply_to(message, "✅ Đã xúc xí ngầu và gửi kết quả đến group!", parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi xúc: {str(e)}")

# ========== XỬ LÝ RÚT TIỀN ==========
@bot.message_handler(func=lambda message: get_player_name(message) in pending_withdraws)
def handle_withdraw_steps(message):
    player_name = get_player_name(message)
    if player_name not in pending_withdraws:
        return
        
    step_data = pending_withdraws[player_name]
    current_step = step_data['step']
    
    try:
        if current_step == 'amount':
            amount = parse_amount(message.text)
            
            if amount < 50000:
                bot.reply_to(message, "❌ Số tiền rút tối thiểu là 50,000 VND!")
                return
                
            balance = game.get_player_balance(player_name)
            if amount > balance:
                bot.reply_to(message, f"❌ Số dư không đủ! Hiện có: {balance:,} VND", parse_mode='HTML')
                return
                
            step_data['amount'] = amount
            step_data['step'] = 'bank_name'
            
            bot.reply_to(message, 
                         "🏦 <b>Bước 2:</b> Nhập tên ngân hàng\n"
                         "Ví dụ: Vietcombank, Techcombank, BIDV, Agribank...", 
                         parse_mode='HTML')
                         
        elif current_step == 'bank_name':
            bank_name = message.text.strip()
            if len(bank_name) < 2:
                bot.reply_to(message, "❌ Tên ngân hàng không hợp lệ! Vui lòng nhập lại.")
                return
                
            step_data['bank_name'] = bank_name
            step_data['step'] = 'bank_account'
            
            bot.reply_to(message,
                         "📋 <b>Bước 3:</b> Nhập số tài khoản\n"
                         "Ví dụ: 1234567890", 
                         parse_mode='HTML')
                         
        elif current_step == 'bank_account':
            bank_account = message.text.strip()
            if not re.match(r'^\d+$', bank_account):
                bot.reply_to(message, "❌ Số tài khoản chỉ được chứa số! Vui lòng nhập lại.")
                return
                
            step_data['bank_account'] = bank_account
            step_data['step'] = 'account_holder'
            
            bot.reply_to(message,
                         "👨‍💼 <b>Bước 4:</b> Nhập tên chủ tài khoản (VIẾT HOA KHÔNG DẤU)\n"
                         "Ví dụ: NGUYEN VAN A", 
                         parse_mode='HTML')
                         
        elif current_step == 'account_holder':
            account_holder = message.text.strip().upper()
            if len(account_holder) < 2:
                bot.reply_to(message, "❌ Tên chủ tài khoản không hợp lệ! Vui lòng nhập lại.")
                return
                
            step_data['account_holder'] = account_holder
            
            confirm_text = f"""
✅ <b>XÁC NHẬN THÔNG TIN RÚT TIỀN</b>

💰 <b>Số tiền:</b> {step_data['amount']:,} VND
🏦 <b>Ngân hàng:</b> {step_data['bank_name']}
📋 <b>Số tài khoản:</b> {step_data['bank_account']}
👨‍💼 <b>Chủ tài khoản:</b> {step_data['account_holder']}

Gõ <b>YES</b> để xác nhận hoặc <b>NO</b> để hủy
            """
            
            bot.reply_to(message, confirm_text, parse_mode='HTML')
            step_data['step'] = 'confirmation'
            
        elif current_step == 'confirmation':
            if message.text.upper() == 'YES':
                success, result_msg = game.request_withdraw(
                    player_name,
                    step_data['amount'],
                    step_data['bank_account'],
                    step_data['bank_name'],
                    step_data['account_holder']
                )
                
                bot.reply_to(message, result_msg, parse_mode='HTML')
                
            elif message.text.upper() == 'NO':
                bot.reply_to(message, "❌ Đã hủy yêu cầu rút tiền!")
            else:
                bot.reply_to(message, "❌ Vui lòng gõ YES để xác nhận hoặc NO để hủy!")
                return
                
            del pending_withdraws[player_name]
                
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi xử lý: {str(e)}")
        if player_name in pending_withdraws:
            del pending_withdraws[player_name]

# ========== XỬ LÝ TIN NHẮN ==========
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.lower()
    
    if text in ['hi', 'hello', 'chào', 'xin chào']:
        if is_private_chat(message) and is_admin(message):
            bot.reply_to(message, "🛠️ Chào admin! Sử dụng các lệnh admin để quản lý game.")
        else:
            bot.reply_to(message, "👋 Chào bạn! Gõ /start để xem hướng dẫn game Tài Xỉu!")
    elif text in ['admin', 'quản trị']:
        if is_private_chat(message) and is_admin(message):
            bot.reply_to(message, "🛠️ Bạn đang trong khu vực quản trị. Sử dụng các lệnh admin để quản lý.")
        else:
            bot.reply_to(message, "❌ Bạn không có quyền truy cập khu vực quản trị!")
    elif text in ['random', 'ngẫu nhiên', 'có thể đoán được không']:
        bot.reply_to(message, "🎲 Kết quả game hoàn toàn ngẫu nhiên và không thể dự đoán! Gõ /xacsuat để xem thông tin xác suất.")
    else:
        bot.reply_to(message, "🤔 Không hiểu lệnh! Gõ /start để xem hướng dẫn.")

if __name__ == "__main__":
    print("🎰 Bot Tài Xỉu đang khởi động...")
    print("🎲 Logic ngẫu nhiên: KẾT QUẢ KHÔNG THỂ ĐOÁN TRƯỚC")
    print(f"🤖 Token: {BOT_TOKEN[:10]}...")
    print(f"👥 Group Chat ID: {CHAT_ID}")
    print(f"👮 Admin ID: {ADMIN_USER_ID}")
    print("🚀 Bot đã sẵn sàng!")
    
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"❌ Lỗi khởi động bot: {e}")
        print("🔄 Đang thử khởi động lại...")
        import time
        time.sleep(5)
        bot.polling(none_stop=True)
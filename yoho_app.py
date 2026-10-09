
import os
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yoho_ultimate_enterprise_key'
socketio = SocketIO(app, cors_allowed_origins="*")

active_rooms = {
    "885522": {
        "id": "885522", 
        "title": "👑 VIP Ejderha & Müzik Odası", 
        "owner": "Kral Yakup", 
        "online": 4810, 
        "vip": 18,
        "category": "Müzik", 
        "password": "",
        "pinned_msg": "📌 Duyuru: Hoş geldiniz! Kurallara uymayı unutmayalım.",
        "users": [], 
        "seats": {i: None for i in range(1, 9)},
        "banned": [],
        "muted_users": []
    }
}

HTML_CODE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yoho Global Live - Enterprise Ultimate Pro</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        :root {
            --bg-dark: #000005;
            --card-bg: #09091c;
            --accent-pink: #ff2a5f;
            --gold: #ffc107;
            --neon-blue: #00f2fe;
            --border-color: #1c1c42;
        }
        body { background: var(--bg-dark); color: #fff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding-bottom: 75px; user-select: none; overflow-x: hidden; }
        
        #authScreen {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at center, #420d85 0%, #000005 100%);
            z-index: 99999; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 20px; box-sizing: border-box; overflow-y: auto;
        }
        .auth-card {
            background: rgba(9, 9, 28, 0.98); border: 1px solid #bc35ff; border-radius: 24px; padding: 25px; width: 100%; max-width: 380px; text-align: center;
            box-shadow: 0 45px 120px rgba(0,0,0,0.99);
        }
        .auth-card h2 { color: var(--gold); margin-bottom: 5px; font-size: 26px; text-shadow: 0 0 20px rgba(255,193,7,0.9); }
        .auth-card p { color: #8a8a9e; font-size: 12px; margin-bottom: 15px; }

        .input-group { margin-bottom: 12px; text-align: left; }
        .input-group label { font-size: 11px; color: #a2a2b5; display: block; margin-bottom: 4px; font-weight: 600; }
        .input-field { width: 100%; padding: 11px 14px; background: #000005; border: 1px solid var(--border-color); border-radius: 12px; color: #fff; font-size: 13px; box-sizing: border-box; }
        .input-field:focus { border-color: var(--gold); outline: none; box-shadow: 0 0 12px rgba(255,193,7,0.5); }
        
        .btn-gold { background: linear-gradient(45deg, #ffd700, #ff8c00); color: #000; width: 100%; padding: 12px; border-radius: 12px; font-size: 13px; font-weight: bold; border: none; cursor: pointer; box-shadow: 0 4px 15px rgba(255,193,7,0.4); margin-top: 10px; }

        #lobbyScreen { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: var(--bg-dark); z-index: 9999; overflow-y: auto; padding: 15px; box-sizing: border-box; }
        .lobby-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; }
        
        .ai-banner { background: linear-gradient(135deg, #76199e, #00f2fe); border-radius: 16px; padding: 12px 15px; margin-bottom: 15px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 8px 20px rgba(0,242,254,0.2); cursor: pointer; }
        
        .category-bar { display: flex; gap: 8px; margin-bottom: 15px; overflow-x: auto; padding-bottom: 5px; }
        .cat-btn { background: var(--card-bg); border: 1px solid var(--border-color); color: #aaa; padding: 6px 12px; border-radius: 15px; font-size: 11px; cursor: pointer; white-space: nowrap; }
        .cat-btn.active { background: #76199e; border-color: var(--gold); color: var(--gold); font-weight: bold; }

        .room-card-item { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 15px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: 0.2s; }
        .room-card-item:hover { border-color: var(--gold); background: #141438; }

        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 999999; justify-content: center; align-items: center; }
        .modal-box { background: var(--card-bg); border: 1px solid #bc35ff; border-radius: 20px; padding: 20px; width: 85%; max-width: 340px; text-align: center; }

        .header { background: var(--card-bg); padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); position: sticky; top: 0; z-index: 100; }
        .room-info h3 { margin: 0; font-size: 14px; color: #fff; display: flex; align-items: center; gap: 5px; }
        .room-info p { margin: 2px 0 0; font-size: 10px; color: #8a8a9e; }
        .room-actions-top { display: flex; gap: 6px; align-items: center; }
        .badge-btn { background: linear-gradient(45deg, #ff2a5f, #7928ca); padding: 4px 10px; border-radius: 20px; font-size: 10px; font-weight: bold; cursor: pointer; color: #fff; border: none; }
        .vip-badge { background: linear-gradient(45deg, #ffd700, #ff8c00); color: #000; padding: 4px 10px; border-radius: 20px; font-size: 10px; font-weight: 900; }

        .online-users-tray { display: flex; gap: 10px; overflow-x: auto; padding: 10px 15px; background: rgba(9,9,28,0.95); border-bottom: 1px solid var(--border-color); align-items: center; }
        .online-user-card { display: flex; flex-direction: column; align-items: center; cursor: pointer; flex-shrink: 0; transition: 0.2s; }
        .online-user-card:hover { transform: scale(1.08); }
        .online-user-avatar-wrap { width: 44px; height: 44px; position: relative; }
        .online-user-avatar { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; background: #76199e; display: flex; align-items: center; justify-content: center; font-size: 18px; position: absolute; top: 2px; left: 2px; border: 2px solid var(--gold); box-shadow: 0 0 10px rgba(255,193,7,0.5); }
        .online-user-frame { position: absolute; top: -2px; left: -2px; width: 48px; height: 48px; border-radius: 50%; border: 2px solid var(--neon-blue); animation: rotateFrame 6s linear infinite; pointer-events: none; }
        @keyframes rotateFrame { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .online-user-name { font-size: 9px; color: #ccc; margin-top: 3px; max-width: 50px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

        .marquee-container { background: rgba(255,193,7,0.15); border-bottom: 1px solid rgba(255,193,7,0.3); overflow: hidden; white-space: nowrap; padding: 5px 0; font-size: 11px; color: var(--gold); }
        .marquee-text { display: inline-block; animation: marquee 20s linear infinite; }
        @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }

        .pinned-banner { background: rgba(0,242,254,0.12); border-bottom: 1px solid rgba(0,242,254,0.3); padding: 6px 12px; font-size: 11px; color: var(--neon-blue); display: flex; justify-content: space-between; align-items: center; }

        .tab-content { display: none; padding: 12px; }
        .tab-content.active { display: block; }

        .theme-selector { display: flex; gap: 6px; margin-bottom: 10px; justify-content: center; overflow-x: auto; padding-bottom: 5px; }
        .theme-btn { background: var(--card-bg); border: 1px solid var(--border-color); color: #ccc; padding: 5px 10px; border-radius: 12px; font-size: 11px; cursor: pointer; white-space: nowrap; }
        .theme-btn.active { border-color: var(--gold); color: var(--gold); background: #76199e; }

        .seats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; max-width: 420px; margin: 10px auto; padding: 12px; background: rgba(9, 9, 28, 0.85); border-radius: 20px; border: 1px solid var(--border-color); }
        .seat { background: #000005; border: 2px dashed #2a2a40; border-radius: 50%; width: 64px; height: 64px; margin: auto; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; cursor: pointer; transition: 0.3s; overflow: hidden; }
        .seat.occupied { border: 2px solid var(--gold); background: #1c160b; box-shadow: 0 0 12px rgba(255,193,7,0.4); }
        .seat span { font-size: 9px; position: absolute; bottom: -18px; width: 75px; text-align: center; color: #b0b0c3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .mic-status { position: absolute; bottom: 0; right: 0; background: #2ed573; font-size: 8px; padding: 2px 4px; border-radius: 50%; border: 1px solid #111; z-index: 2; }
        .seat-number { position: absolute; top: -2px; left: -2px; background: #1c1c42; font-size: 8px; padding: 1px 4px; border-radius: 50%; color: #888; z-index: 2; }

        .audio-wave { display: flex; align-items: center; gap: 2px; height: 10px; position: absolute; bottom: 4px; z-index: 3; }
        .wave-bar { width: 2px; background: var(--neon-blue); border-radius: 2px; animation: wave 0.8s infinite ease-in-out; }
        .wave-bar:nth-child(2) { animation-delay: 0.2s; }
        .wave-bar:nth-child(3) { animation-delay: 0.4s; }
        @keyframes wave { 0%, 100% { height: 3px; } 50% { height: 12px; } }

        .dj-box { background: linear-gradient(135deg, #420d85, #09091c); border: 1px solid #bc35ff; border-radius: 14px; padding: 10px 12px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; }
        .dj-info { font-size: 11px; color: #d0c4f0; }
        .dj-info b { color: var(--gold); display: block; font-size: 12px; }

        .mystery-box-banner { background: linear-gradient(45deg, #ff2a5f, #ffc107); border-radius: 12px; padding: 8px 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; font-size: 12px; font-weight: bold; color: #000; cursor: pointer; animation: pulseBox 2s infinite; }
        @keyframes pulseBox { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }

        .chat-container { height: 130px; background: var(--card-bg); margin: 8px 0; border-radius: 14px; padding: 10px; overflow-y: auto; font-size: 12px; border: 1px solid var(--border-color); display: flex; flex-direction: column; gap: 6px; }
        .chat-msg { line-height: 1.4; word-break: break-all; background: rgba(0,0,0,0.3); padding: 5px 8px; border-radius: 8px; }
        .chat-msg b { color: var(--neon-blue); }
        .chat-msg.gift { background: rgba(255,193,7,0.12); border-left: 3px solid var(--gold); }
        .chat-msg.entrance { background: rgba(0,242,254,0.2); border-left: 3px solid var(--neon-blue); font-weight: bold; }

        .chat-input-bar { display: flex; gap: 8px; margin-top: 8px; }
        .chat-input { flex: 1; padding: 10px 14px; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 20px; color: #fff; font-size: 12px; }
        .chat-input:focus { outline: none; border-color: var(--neon-blue); }

        .control-bar { display: flex; gap: 6px; justify-content: center; margin-top: 8px; flex-wrap: wrap; }
        .btn { background: #ff2a5f; border: none; color: white; padding: 8px 12px; border-radius: 20px; font-size: 11px; cursor: pointer; font-weight: bold; display: flex; align-items: center; gap: 4px; box-shadow: 0 4px 10px rgba(255,42,95,0.3); }
        .btn:active { transform: scale(0.95); }
        .btn-gold { background: linear-gradient(45deg, #ffd700, #ff8c00); color: #000; box-shadow: 0 4px 10px rgba(255,193,7,0.3); }
        .btn-dark { background: var(--card-bg); border: 1px solid var(--border-color); color: #ccc; }

        .bottom-nav { position: fixed; bottom: 0; width: 100%; background: #000005; display: flex; justify-content: space-around; padding: 8px 0; border-top: 1px solid var(--border-color); z-index: 1000; box-sizing: border-box; }
        .nav-item { text-align: center; color: #73738c; font-size: 10px; cursor: pointer; flex: 1; }
        .nav-item.active { color: var(--gold); }
        .nav-item div { font-size: 18px; margin-bottom: 2px; }

        .card { background: var(--card-bg); padding: 14px; border-radius: 16px; margin-bottom: 12px; border: 1px solid var(--border-color); }
        .card h4 { margin: 0 0 10px 0; color: var(--gold); display: flex; justify-content: space-between; align-items: center; font-size: 14px; }
        .item-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--border-color); font-size: 12px; }

        @keyframes diamondRain { 0% { transform: translateY(-50px) rotate(0deg); opacity: 1; } 100% { transform: translateY(100vh) rotate(360deg); opacity: 0; } }
        .falling-diamond { position: fixed; top: -50px; z-index: 999999; animation: diamondRain 2.5s linear forwards; font-size: 24px; pointer-events: none; }
    </style>
</head>
<body id="appBody">

    <div id="authScreen">
        <div class="auth-card">
            <h2>👑 Yoho Enterprise Ultimate</h2>
            <p>Profesyonel Canlı Ses & Eğlence Platformu</p>
            
            <div class="input-group">
                <label>Kullanıcı Adınız</label>
                <input type="text" id="loginNickInput" class="input-field" value="Kral Yakup">
            </div>
            
            <button class="btn-gold" onclick="instantLogin()">⚡ Anında Giriş Yap ve Başla</button>
        </div>
    </div>

    <div id="lobbyScreen">
        <div class="lobby-header">
            <div>
                <h2 style="margin:0; color:var(--gold);">🌐 Canlı Ses Odaları Lobi</h2>
                <p style="margin:2px 0 0; font-size:11px; color:#8a8a9e;">Kendi odanı kur veya aktif odalara katıl!</p>
            </div>
            <button class="btn btn-gold" onclick="openCreateRoomModal()">+ Oda Kur</button>
        </div>

        <div class="ai-banner" onclick="openAiAssistantModal()">
            <div>
                <b>🤖 Global AI Asistanı</b>
                <p style="margin:2px 0 0; font-size:10px; color:#d0c4f0;">Yapay zeka ile odaları yönet!</p>
            </div>
            <button class="btn btn-gold" style="padding:6px 12px; font-size:11px;">Sohbet Et</button>
        </div>

        <div style="display:flex; gap:10px; margin-bottom:15px;">
            <button class="btn btn-gold" style="flex:1; justify-content:center;" onclick="openDailyCheckinModal()">🎁 Günlük Ödül</button>
            <button class="btn btn-dark" style="flex:1; justify-content:center;" onclick="openAgencyModal()">🏛️ Ajans & Lonca</button>
        </div>

        <div class="category-bar">
            <button class="cat-btn active" onclick="filterCategory('Tümü', this)">🔥 Tümü</button>
            <button class="cat-btn" onclick="filterCategory('Müzik', this)">🎧 Müzik</button>
            <button class="cat-btn" onclick="filterCategory('Sohbet', this)">💬 Sohbet</button>
        </div>

        <div id="roomListContainer"></div>
    </div>

    <!-- PROFİL DÜZENLEME MODALI -->
    <div class="modal-overlay" id="editProfileModal" onclick="closeModalBg(event, 'editProfileModal')">
        <div class="modal-box">
            <h3 style="color:var(--gold); margin-top:0;">✏️ Profil Bilgilerini Düzenle</h3>
            <div class="input-group">
                <label>Kullanıcı Adı</label>
                <input type="text" id="editNickInput" class="input-field" value="Kral Yakup">
            </div>
            <div class="input-group">
                <label>Avatar / Emoji</label>
                <input type="text" id="editAvatarInput" class="input-field" value="👑">
            </div>
            <button class="btn btn-gold" style="width:100%; justify-content:center; margin-bottom:8px;" onclick="saveProfileChanges()">Kaydet ve Güncelle 🚀</button>
            <button class="btn btn-dark" style="width:100%; justify-content:center;" onclick="document.getElementById('editProfileModal').style.display='none'">İptal</button>
        </div>
    </div>

    <!-- ODA AYARLARI MODALI -->
    <div class="modal-overlay" id="roomSettingsModal" onclick="closeModalBg(event, 'roomSettingsModal')">
        <div class="modal-box">
            <h3 style="color:var(--gold); margin-top:0;">⚙️ Oda Ayarları & Şifre</h3>
            <div class="input-group">
                <label>Oda Başlığı</label>
                <input type="text" id="settingsRoomTitle" class="input-field" value="👑 VIP Ejderha & Müzik Odası">
            </div>
            <div class="input-group">
                <label>Oda Şifresi</label>
                <input type="text" id="settingsRoomPassword" class="input-field" placeholder="Örn: 1234">
            </div>
            <button class="btn btn-gold" style="width:100%; justify-content:center; margin-bottom:8px;" onclick="saveRoomSettings()">Ayarları Kaydet</button>
            <button class="btn btn-dark" style="width:100%; justify-content:center;" onclick="document.getElementById('roomSettingsModal').style.display='none'">Kapat</button>
        </div>
    </div>

    <!-- MODERATÖR & YÖNETİM MODALI -->
    <div class="modal-overlay" id="modActionModal" onclick="closeModalBg(event, 'modActionModal')">
        <div class="modal-box">
            <h3 style="color:var(--gold); margin-top:0;">🛡️ Oda Yönetim Paneli</h3>
            <p id="modTargetName" style="color:var(--neon-blue); font-weight:bold; margin-bottom:15px;"></p>
            <div style="display:flex; flex-direction:column; gap:8px;">
                <button class="btn btn-dark" style="justify-content:center; background:#ff2a5f;" onclick="executeModAction('kick')">👢 Koltuktan / Odadan At (Kick)</button>
                <button class="btn btn-dark" style="justify-content:center; background:#e67e22;" onclick="executeModAction('mute')">🔇 Mikrofonu Sustur (Mute)</button>
                <button class="btn btn-dark" style="justify-content:center; background:#c0392b;" onclick="executeModAction('ban')">🔨 Odayı Yasakla (Ban)</button>
            </div>
            <button class="btn btn-dark" style="width:100%; justify-content:center; margin-top:10px;" onclick="document.getElementById('modActionModal').style.display='none'">İptal</button>
        </div>
    </div>

    <!-- ODA KURMA MODALI -->
    <div class="modal-overlay" id="createRoomModal" onclick="closeModalBg(event, 'createRoomModal')">
        <div class="modal-box">
            <h3 style="color:var(--gold); margin-top:0;">Yeni Ses Odası Kur</h3>
            <div class="input-group" style="margin-bottom:10px;">
                <label>Oda Başlığı</label>
                <input type="text" id="newRoomTitle" class="input-field" value="👑 Kral Yakup'un Odası">
            </div>
            <button class="btn btn-gold" style="width:100%; justify-content:center; margin-bottom:8px;" onclick="createNewRoom()">Odayı Başlat 🚀</button>
            <button class="btn btn-dark" style="width:100%; justify-content:center;" onclick="document.getElementById('createRoomModal').style.display='none'">İptal</button>
        </div>
    </div>

    <!-- AJANS MODALI -->
    <div class="modal-overlay" id="agencyModal" onclick="closeModalBg(event, 'agencyModal')">
        <div class="modal-box">
            <h3 style="color:var(--gold); margin-top:0;">🏛️ Ajans & Lonca Yönetimi</h3>
            <div style="background:#000005; padding:10px; border-radius:10px; margin-bottom:12px; text-align:left; font-size:11px; border:1px solid var(--border-color);">
                <div><b>Kral Ajans 👑</b></div>
                <div style="color:#888;">Kurucu: Kral Yakup • Üye: 1,420</div>
            </div>
            <button class="btn btn-dark" style="width:100%; justify-content:center;" onclick="document.getElementById('agencyModal').style.display='none'">Kapat</button>
        </div>
    </div>

    <!-- GÜNLÜK ÖDÜL MODALI -->
    <div class="modal-overlay" id="dailyModal" onclick="closeModalBg(event, 'dailyModal')">
        <div class="modal-box">
            <h3 style="color:var(--gold); margin-top:0;">🎁 Günlük Giriş Ödülü</h3>
            <div style="background:#000005; padding:15px; border-radius:12px; margin-bottom:15px; border:1px solid var(--border-color);">
                <div style="font-size:22px; color:var(--gold); font-weight:bold;">💎 +10,000,000 Elmas</div>
            </div>
            <button class="btn btn-gold" style="width:100%; justify-content:center; margin-bottom:8px;" onclick="claimDailyReward()">Ödülü Topla 🚀</button>
            <button class="btn btn-dark" style="width:100%; justify-content:center;" onclick="document.getElementById('dailyModal').style.display='none'">Kapat</button>
        </div>
    </div>

    <!-- PK SAVAŞ MODALI -->
    <div class="modal-overlay" id="pkModal" onclick="closeModalBg(event, 'pkModal')">
        <div class="modal-box">
            <h3 style="color:var(--gold); margin-top:0;">⚔️ Canlı PK Savaş Arenası</h3>
            <div style="background:#000005; padding:12px; border-radius:10px; margin-bottom:15px; border:1px solid var(--border-color); text-align:center;">
                <div style="font-size:12px; color:var(--neon-blue); margin-bottom:5px;">⏳ Kalan Süre: <b id="pkTimer">03:00</b></div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div><b>Bizim Oda</b><br><span style="color:var(--gold); font-size:15px;" id="ourPkScore">1,450,200</span></div>
                    <div style="color:var(--accent-pink); font-weight:bold;">VS</div>
                    <div><b>Rakip Oda</b><br><span style="color:#ff2a5f; font-size:15px;" id="rivalPkScore">1,380,000</span></div>
                </div>
            </div>
            <button class="btn btn-gold" style="width:100%; justify-content:center; margin-bottom:8px;" onclick="boostPkScore()">🎁 Destek Gönder (+500,000 Puan)</button>
            <button class="btn btn-dark" style="width:100%; justify-content:center;" onclick="document.getElementById('pkModal').style.display='none'">Kapat</button>
        </div>
    </div>

    <div class="header" id="roomHeader" style="display:none;">
        <div class="room-info">
            <h3 id="roomTitleText">👑 VIP Ejderha & Müzik Odası</h3>
            <p><span id="currentRoomId">ID: 885522</span> • <span style="color:var(--neon-blue); font-weight:bold;">👥 <span id="onlineCounter">4,810</span> Çevrimiçi</span> <button onclick="backToLobby()" style="background:none; border:none; color:var(--gold); cursor:pointer; font-weight:bold; margin-left:5px;">[Lobi]</button></p>
        </div>
        <div class="room-actions-top">
            <button class="badge-btn" onclick="document.getElementById('pkModal').style.display='flex'">⚔️ PK</button>
            <div class="vip-badge" id="vipBadgeTop">VIP 18</div>
        </div>
    </div>

    <div class="online-users-tray" id="onlineUsersTray" style="display:none;"></div>

    <div class="pinned-banner" id="pinnedBanner">
        <span id="pinnedTextContent">📌 Duyuru: Hoş geldiniz! Kurallara uymayı unutmayalım.</span>
        <button style="background:none; border:none; color:var(--gold); cursor:pointer; font-size:10px;" onclick="pinNewMessagePrompt()">[Düzenle]</button>
    </div>

    <div class="marquee-container" id="marqueeBar" style="display:none;">
        <div class="marquee-text" id="marqueeTextContent">✨ Hoş geldiniz! Kral Yakup odaya Lüks Yat ile giriş yaptı! 🛥️ • DJ Kabininden canlı müzik yayını aktif!</div>
    </div>

    <!-- ODA SEKMESİ -->
    <div id="tab-oda" class="tab-content">
        <div class="theme-selector">
            <button class="theme-btn active" onclick="setTheme('default', this)">Klasik</button>
            <button class="theme-btn" onclick="setTheme('neon', this)">Neon Mor</button>
            <button class="theme-btn" onclick="setTheme('galaxy', this)">Galaksi</button>
            <button class="theme-btn" onclick="setTheme('gold', this)">Altın Sarayı</button>
        </div>

        <div class="mystery-box-banner" onclick="claimMysteryBox()">
            <span>🎁 Sürpriz Elmas Sandığı Açıldı! Tıkla Kazan!</span>
            <span style="background:#000; color:#ffc107; padding:3px 8px; border-radius:10px; font-size:10px;">+10M Elmas</span>
        </div>

        <!-- MÜZİK ÇALAR & DJ KABİNİ -->
        <div class="dj-box">
            <div class="dj-info">
                <b>🎧 Canlı Oda DJ Kabini</b>
                <span id="currentSongName" style="color:#aaa;">Çalıyor: _Sen Aşksın_(WJRzcg6WPMU).m4a</span>
            </div>
            <div>
                <input type="file" id="audioFileInput" accept="audio/*" style="display:none;" onchange="uploadAndPlayMusic(event)">
                <button class="btn btn-gold" onclick="document.getElementById('audioFileInput').click()">🎵 Müzik Yükle</button>
                <audio id="roomAudioPlayer" style="display:none;" controls loop></audio>
            </div>
        </div>

        <div class="seats-grid" id="seatsContainer"></div>

        <div class="chat-container" id="chatBox">
            <div class="chat-msg"><b>Sistem:</b> Hoş geldiniz! Kral Yakup odaya Lüks Yat ile giriş yaptı! 🛥️</div>
            <div class="chat-msg gift"><b>Mert:</b> Odaya Yat 🛥️ gönderdi!</div>
            <div class="chat-msg gift"><b>Mert:</b> Odaya 10,000 Elmaslık Şans Zarfı bıraktı! Tıkla ve kap!</div>
        </div>

        <div class="chat-input-bar">
            <input type="text" id="chatInput" class="chat-input" placeholder="Herkese açık mesaj yaz..." onkeypress="checkEnter(event)">
            <button class="btn" onclick="sendChatMsg()">Gönder</button>
        </div>

        <div class="control-bar">
            <button class="btn btn-dark" id="micBtn" onclick="toggleMic()">🎙️ Mikrofon</button>
            <button class="btn btn-gold" onclick="sendGiftAction('Yat')">🛥️ Yat</button>
            <button class="btn btn-gold" onclick="dropRedEnvelope()">🧧 Zarf At</button>
            <button class="btn btn-dark" onclick="document.getElementById('roomSettingsModal').style.display='flex'">⚙️ Oda Ayarla</button>
        </div>
    </div>

    <!-- OYUNLAR SEKMESİ -->
    <div id="tab-oyunlar" class="tab-content">
        <div class="card">
            <h4>🎮 Mini Oyun Salonu</h4>
            <div class="item-row"><span>🎣 Balık Avı Turnuvası</span><button class="btn btn-gold" onclick="alert('Balık avı ödülü alındı: +50M Elmas!')">Oyna</button></div>
            <div class="item-row"><span>🎰 Şans Çarkı</span><button class="btn btn-gold" onclick="alert('Çark çevrildi!')">Çevir</button></div>
        </div>
    </div>

    <!-- SIRALAMALAR SEKMESİ -->
    <div id="tab-siralamalar" class="tab-content">
        <div class="card">
            <h4>👑 Global Zenginler Liderliği</h4>
            <div class="item-row"><span>1. Kral Yakup</span><span style="color:var(--gold);">25,504,450,000 Elmas</span></div>
            <div class="item-row"><span>2. Sultan Asena</span><span style="color:var(--gold);">19,812,820,100 Elmas</span></div>
        </div>
    </div>

    <!-- MAĞAZA SEKMESİ -->
    <div id="tab-magaza" class="tab-content">
        <div class="card">
            <h4>🛍️ VIP & Çerçeve Mağazası</h4>
            <div class="item-row"><span>👑 Kraliyet Çerçevesi</span><button class="btn btn-gold" onclick="buyItem('Kraliyet Çerçevesi', 1000000)">1M Elmas</button></div>
            <div class="item-row"><span>🚗 Süper Spor Araba</span><button class="btn btn-gold" onclick="buyItem('Süper Spor Araba', 5000000)">5M Elmas</button></div>
        </div>
    </div>

    <!-- ÇANTAM SEKMESİ -->
    <div id="tab-canta" class="tab-content">
        <div class="card">
            <h4>🎒 Eşya Envanterim (Çanta)</h4>
            <div id="inventoryList" style="font-size:12px; color:#aaa; text-align:center; padding:15px;">
                Henüz envanterinizde özel eşya bulunmuyor. Mağazadan eşya satın alabilirsiniz!
            </div>
        </div>
    </div>

    <!-- PROFİL SEKMESİ -->
    <div id="tab-profil" class="tab-content">
        <div class="card" style="text-align:center;">
            <div id="profileAvatarDisplay" style="width:80px; height:80px; margin:auto; border-radius:50%; background:#76199e; display:flex; align-items:center; justify-content:center; font-size:40px; border:2px solid var(--gold);">👑</div>
            <h3 id="profileNick" style="margin:8px 0 2px 0; color:var(--gold);">Kral Yakup</h3>
            <p style="font-size:10px; color:#666;">UID: 100001 • VIP 18 • Seviye: <span id="userLevel">45</span></p>
            <div style="background:#000005; padding:10px; border-radius:10px; margin:10px 0;">
                <strong style="color:var(--gold);">💎 <span id="userDiamonds">5,000,254,200</span> Elmas</strong>
            </div>
            <button class="btn btn-gold" style="width:100%; justify-content:center; margin-bottom:8px;" onclick="document.getElementById('editProfileModal').style.display='flex'">✏️ Profili Düzenle</button>
            <button class="btn btn-dark" style="width:100%; justify-content:center;" onclick="topUpDiamonds()">💎 Elmas Yükle</button>
        </div>
    </div>

    <!-- ALT NAVİGASYON ÇUBUĞU -->
    <div class="bottom-nav" id="bottomNav" style="display:none;">
        <div class="nav-item active" onclick="switchTab('oda', this)"><div>🏠</div>Oda</div>
        <div class="nav-item" onclick="switchTab('oyunlar', this)"><div>🎮</div>Oyun</div>
        <div class="nav-item" onclick="switchTab('siralamalar', this)"><div>🏆</div>Lider</div>
        <div class="nav-item" onclick="switchTab('magaza', this)"><div>🛍️</div>Mağaza</div>
        <div class="nav-item" onclick="switchTab('canta', this)"><div>🎒</div>Çanta</div>
        <div class="nav-item" onclick="switchTab('profil', this)"><div>👤</div>Profil</div>
    </div>

    <script>
        const socket = io();
        let userData = { name: "Kral Yakup", avatar: "👑", diamonds: 5000254200, level: 45, inventory: [] };
        let currentRoomId = "885522";
        let micActive = false;
        let localAudioStream = null;
        let roomSeatsData = {1:null, 2:null, 3:null, 4:null, 5:null, 6:null, 7:null, 8:null};
        let currentSelectedTarget = null;
        let roomPassword = "";

        function instantLogin() {
            const nick = document.getElementById('loginNickInput').value.trim();
            if(nick) userData.name = nick;
            
            document.getElementById('authScreen').style.display = 'none';
            document.getElementById('lobbyScreen').style.display = 'block';
            document.getElementById('profileNick').innerText = userData.name;
            loadRooms();
        }

        function loadRooms() {
            fetch('/api/rooms').then(res => res.json()).then(rooms => {
                const container = document.getElementById('roomListContainer');
                container.innerHTML = '';
                rooms.forEach(r => {
                    container.innerHTML += `
                        <div class="room-card-item" onclick="joinRoom('${r.id}', '${r.title}')">
                            <div>
                                <h4 style="margin:0 0 5px 0; color:var(--gold);">${r.title}</h4>
                                <p style="margin:0; font-size:11px; color:#888;">Kurucu: ${r.owner} • Kategori: ${r.category}</p>
                            </div>
                            <div style="font-size:12px; color:var(--neon-blue);">👥 ${r.online.toLocaleString()}</div>
                        </div>
                    `;
                });
            });
        }

        function openCreateRoomModal() {
            document.getElementById('createRoomModal').style.display = 'flex';
        }

        function createNewRoom() {
            const titleInput = document.getElementById('newRoomTitle').value.trim();
            if(!titleInput) return alert("Oda başlığı boş olamaz!");

            fetch('/api/create-room', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: titleInput, owner: userData.name })
            }).then(res => res.json()).then(data => {
                if(data.success) {
                    document.getElementById('createRoomModal').style.display = 'none';
                    joinRoom(data.roomId, titleInput);
                }
            });
        }

        function joinRoom(roomId, roomTitle) {
            currentRoomId = roomId;
            document.getElementById('roomTitleText').innerText = roomTitle;
            document.getElementById('currentRoomId').innerText = 'ID: ' + roomId;
            
            document.getElementById('lobbyScreen').style.display = 'none';
            document.getElementById('roomHeader').style.display = 'flex';
            document.getElementById('onlineUsersTray').style.display = 'flex';
            document.getElementById('marqueeBar').style.display = 'block';
            document.getElementById('bottomNav').style.display = 'flex';
            document.getElementById('tab-oda').classList.add('active');

            socket.emit('join_room', { room: roomId, user: userData });
        }

        function backToLobby() {
            if(micActive) toggleMic();
            socket.emit('leave_room', { room: currentRoomId, user: userData });
            
            document.getElementById('roomHeader').style.display = 'none';
            document.getElementById('onlineUsersTray').style.display = 'none';
            document.getElementById('marqueeBar').style.display = 'none';
            document.getElementById('bottomNav').style.display = 'none';
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            document.getElementById('lobbyScreen').style.display = 'block';
            loadRooms();
        }

        function saveProfileChanges() {
            const newNick = document.getElementById('editNickInput').value.trim();
            const newAvatar = document.getElementById('editAvatarInput').value.trim();
            if(newNick) userData.name = newNick;
            if(newAvatar) userData.avatar = newAvatar;

            document.getElementById('profileNick').innerText = userData.name;
            document.getElementById('profileAvatarDisplay').innerText = userData.avatar;
            document.getElementById('editProfileModal').style.display = 'none';
            alert("✅ Profil bilgileri güncellendi!");
        }

        function saveRoomSettings() {
            const newTitle = document.getElementById('settingsRoomTitle').value.trim();
            const newPass = document.getElementById('settingsRoomPassword').value.trim();
            if(newTitle) document.getElementById('roomTitleText').innerText = newTitle;
            roomPassword = newPass;
            document.getElementById('roomSettingsModal').style.display = 'none';
            alert("⚙️ Oda ayarları ve şifre başarıyla kaydedildi!");
        }

        function pinNewMessagePrompt() {
            let pMsg = prompt("Odaya sabitlenecek yeni duyuru metnini yazın:");
            if(pMsg) {
                document.getElementById('pinnedTextContent').innerText = "📌 Duyuru: " + pMsg;
                alert("📌 Duyuru odaya sabitlendi!");
            }
        }

        function buyItem(itemName, price) {
            if(userData.diamonds < price) {
                alert("❌ Yetersiz elmas!");
                return;
            }
            userData.diamonds -= price;
            userData.inventory.push(itemName);
            updateDiamondDisplay();
            updateInventoryUI();
            alert(`🎉 Başarıyla satın alındı: ${itemName}! Çantanıza eklendi.`);
        }

        function updateInventoryUI() {
            const invBox = document.getElementById('inventoryList');
            if(userData.inventory.length === 0) return;
            invBox.innerHTML = '';
            userData.inventory.forEach(item => {
                invBox.innerHTML += `<div style="background:#000; padding:10px; border-radius:8px; margin-bottom:5px; border:1px solid var(--gold);">✨ ${item} (Aktif)</div>`;
            });
        }

        socket.on('banned_from_room', () => {
            alert("❌ Bu odadan yasaklandınız!");
            backToLobby();
        });

        socket.on('update_room_users', (data) => {
            const tray = document.getElementById('onlineUsersTray');
            tray.innerHTML = '';
            document.getElementById('onlineCounter').innerText = data.users.length.toLocaleString();
            data.users.forEach(u => {
                tray.innerHTML += `
                    <div class="online-user-card" onclick="inspectUser('${u.name}')">
                        <div class="online-user-avatar-wrap">
                            <div class="online-user-frame"></div>
                            <div class="online-user-avatar">${u.avatar}</div>
                        </div>
                        <span class="online-user-name">${u.name}</span>
                    </div>
                `;
            });
        });

        socket.on('update_seats', (seats) => {
            roomSeatsData = seats;
            renderSeats();
        });

        socket.on('chat_message', (data) => {
            const box = document.getElementById('chatBox');
            let cls = data.type === 'gift' ? 'chat-msg gift' : 'chat-msg';
            box.innerHTML += `<div class="${cls}"><b>${data.sender}:</b> ${data.text}</div>`;
            box.scrollTop = box.scrollHeight;
            if(data.type === 'gift') triggerDiamondRain();
        });

        socket.on('play_music_sync', (data) => {
            const player = document.getElementById('roomAudioPlayer');
            player.src = data.audioUrl;
            player.play();
            document.getElementById('currentSongName').innerText = '🎶 ' + data.songName;
        });

        function uploadAndPlayMusic(event) {
            const file = event.target.files[0];
            if(file) {
                const audioUrl = URL.createObjectURL(file);
                socket.emit('sync_music', { room: currentRoomId, audioUrl: audioUrl, songName: file.name });
            }
        }

        function clickSeat(seatNum) {
            let occupant = roomSeatsData[seatNum];
            if(!occupant) {
                socket.emit('take_seat', { room: currentRoomId, seatNum: seatNum, user: userData });
            } else {
                currentSelectedTarget = occupant.name;
                document.getElementById('modTargetName').innerText = "Hedef Kullanıcı: " + occupant.name;
                document.getElementById('modActionModal').style.display = 'flex';
            }
        }

        function executeModAction(actionType) {
            document.getElementById('modActionModal').style.display = 'none';
            if(!currentSelectedTarget) return;
            socket.emit('mod_action', { room: currentRoomId, target: currentSelectedTarget, action: actionType });
        }

        async function toggleMic() {
            const btn = document.getElementById('micBtn');
            if(!micActive) {
                try {
                    localAudioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    micActive = true;
                    btn.style.background = '#2ed573';
                    btn.style.color = '#000';
                    btn.innerHTML = '🎙️ Canlı';
                    socket.emit('send_chat', { room: currentRoomId, sender: userData.name, text: '🎙️ Mikrofonunu açtı ve sesli yayına başladı!', type: 'entrance' });
                } catch(e) {
                    alert('Mikrofon izni alınamadı.');
                }
            } else {
                if(localAudioStream) localAudioStream.getTracks().forEach(t => t.stop());
                micActive = false;
                btn.style.background = '#09091c';
                btn.style.color = '#ccc';
                btn.innerHTML = '🎙️ Mikrofon';
            }
        }

        function sendGiftAction(giftName) {
            socket.emit('send_chat', { room: currentRoomId, sender: userData.name, text: `oğdaya ${giftName} 🛥️ gönderdi!`, type: 'gift' });
        }

        function dropRedEnvelope() {
            socket.emit('send_chat', { room: currentRoomId, sender: userData.name, text: `oğdaya 10,000 Elmaslık Şans Zarfı bıraktı! Tıkla ve kap!`, type: 'gift' });
        }

        function triggerDiamondRain() {
            for(let i=0; i<25; i++) {
                let d = document.createElement('div');
                d.className = 'falling-diamond';
                d.innerHTML = ['💎', '✨', '🪙', '🌹'][Math.floor(Math.random()*4)];
                d.style.left = Math.random() * window.innerWidth + 'px';
                d.style.animationDuration = (Math.random() * 1.5 + 1.5) + 's';
                document.body.appendChild(d);
                setTimeout(() => d.remove(), 3000);
            }
        }

        function sendChatMsg() {
            const input = document.getElementById('chatInput');
            const txt = input.value.trim();
            if(!txt) return;
            socket.emit('send_chat', { room: currentRoomId, sender: userData.name, text: txt, type: 'text' });
            input.value = '';
        }

        function checkEnter(e) { if(e.key === 'Enter') sendChatMsg(); }

        function inspectUser(name) {
            document.getElementById('modalUserName').innerText = name;
            document.getElementById('userProfileModal').style.display = 'flex';
        }

        function boostPkScore() {
            let our = parseInt(document.getElementById('ourPkScore').innerText.replace(/,/g, '')) + 500000;
            document.getElementById('ourPkScore').innerText = our.toLocaleString();
            socket.emit('send_chat', { room: currentRoomId, sender: userData.name, text: `⚔️ PK Savaşında +500,000 puanlık dev destek sağlandı!`, type: 'gift' });
            document.getElementById('pkModal').style.display = 'none';
        }

        function renderSeats() {
            const seatsGrid = document.getElementById('seatsContainer');
            seatsGrid.innerHTML = '';
            for(let i=1; i<=8; i++) {
                let userInSeat = roomSeatsData[i];
                let occupied = userInSeat !== null && userInSeat !== undefined;
                let seatClass = occupied ? 'seat occupied' : 'seat';
                let occupantName = occupied ? userInSeat.name : 'Boş Koltuk';
                let avatarIcon = occupied ? userInSeat.avatar : '🪑';
                let micHtml = occupied ? '<div class="mic-status">🎙️</div>' : '';
                let waveHtml = (occupied && micActive && userInSeat.name === userData.name) ? '<div class="audio-wave"><div class="wave-bar"></div><div class="wave-bar"></div><div class="wave-bar"></div></div>' : '';

                seatsGrid.innerHTML += `
                    <div class="${seatClass}" onclick="clickSeat(${i})">
                        <div class="seat-number">${i}</div>
                        <div style="font-size:18px;">${avatarIcon}</div>
                        <span style="font-size:9px;">${occupantName}</span>
                        ${micHtml}
                        ${waveHtml}
                    </div>
                `;
            }
        }

        function switchTab(tabId, el) {
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById('tab-' + tabId).classList.add('active');
            if(el) el.classList.add('active');
        }

        function setTheme(theme, el) {
            document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
            if(el) el.classList.add('active');
            const body = document.getElementById('appBody');
            if(theme === 'neon') {
                body.style.setProperty('--bg-dark', '#420d85');
                body.style.setProperty('--card-bg', '#5a14ab');
            } else if(theme === 'galaxy') {
                body.style.setProperty('--bg-dark', '#050b1f');
                body.style.setProperty('--card-bg', '#0f172a');
            } else if(theme === 'gold') {
                body.style.setProperty('--bg-dark', '#1a1400');
                body.style.setProperty('--card-bg', '#2d2300');
                body.style.setProperty('--gold', '#ffdf00');
            } else {
                body.style.setProperty('--bg-dark', '#000005');
                body.style.setProperty('--card-bg', '#09091c');
            }
        }

        function openAgencyModal() { document.getElementById('agencyModal').style.display = 'flex'; }
        function openDailyCheckinModal() { document.getElementById('dailyModal').style.display = 'flex'; }
        function openAiAssistantModal() { alert('🤖 AI Asistan: Canlı odaları optimize ediyor!'); }

        function claimDailyReward() {
            userData.diamonds += 10000000;
            updateDiamondDisplay();
            document.getElementById('dailyModal').style.display = 'none';
            alert('🎁 +10,000,000 Elmas eklendi!');
        }

        function claimMysteryBox() {
            userData.diamonds += 10000000;
            updateDiamondDisplay();
            triggerDiamondRain();
        }

        function topUpDiamonds() {
            userData.diamonds += 10000000000;
            updateDiamondDisplay();
            alert('💎 Elmaslar yüklendi!');
        }

        function updateDiamondDisplay() {
            document.getElementById('userDiamonds').innerText = userData.diamonds.toLocaleString();
        }

        function closeModalBg(e, modalId) {
            if(e.target.id === modalId) document.getElementById(modalId).style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    room_list = [{"id": r["id"], "title": r["title"], "owner": r["owner"], "online": r["online"] + len(r["users"]), "category": r["category"]} for r in active_rooms.values()]
    return jsonify(room_list)

@app.route('/api/create-room', methods=['POST'])
def create_room():
    data = request.json
    room_id = str(random.randint(100000, 999900))
    title = data.get('title', 'Yeni Ses Odası')
    owner = data.get('owner', 'Kullanıcı')
    active_rooms[room_id] = {
        "id": room_id,
        "title": title,
        "owner": owner,
        "online": 1,
        "category": "Sohbet",
        "password": "",
        "pinned_msg": "📌 Duyuru aktif",
        "users": [],
        "seats": {i: None for i in range(1, 9)},
        "banned": []
    }
    return jsonify({"success": True, "roomId": room_id})

@socketio.on('join_room')
def handle_join(data):
    room = data['room']
    user = data['user']
    if room in active_rooms:
        if user.get('name') in active_rooms[room]["banned"]:
            emit('banned_from_room')
            return
        join_room(room)
        if not any(u.get('name') == user.get('name') for u in active_rooms[room]["users"]):
            active_rooms[room]["users"].append(user)
        emit('update_room_users', {"users": active_rooms[room]["users"]}, room=room)
        emit('update_seats', active_rooms[room]["seats"], room=room)

@socketio.on('leave_room')
def handle_leave(data):
    room = data['room']
    user = data['user']
    leave_room(room)
    if room in active_rooms:
        active_rooms[room]["users"] = [u for u in active_rooms[room]["users"] if u.get('name') != user.get('name')]
        for s_idx in active_rooms[room]["seats"]:
            if active_rooms[room]["seats"][s_idx] and active_rooms[room]["seats"][s_idx].get('name') == user.get('name'):
                active_rooms[room]["seats"][s_idx] = None
        emit('update_room_users', {"users": active_rooms[room]["users"]}, room=room)
        emit('update_seats', active_rooms[room]["seats"], room=room)

@socketio.on('take_seat')
def handle_take_seat(data):
    room = data['room']
    seat_num = data['seatNum']
    user = data['user']
    if room in active_rooms:
        for s_idx in active_rooms[room]["seats"]:
            if active_rooms[room]["seats"][s_idx] and active_rooms[room]["seats"][s_idx].get('name') == user.get('name'):
                active_rooms[room]["seats"][s_idx] = None
        
        if active_rooms[room]["seats"].get(seat_num) is None:
            active_rooms[room]["seats"][seat_num] = user
            emit('update_seats', active_rooms[room]["seats"], room=room)

@socketio.on('mod_action')
def handle_mod_action(data):
    room = data['room']
    target_name = data['target']
    action = data['action']
    if room in active_rooms:
        if action == 'ban':
            active_rooms[room]["banned"].append(target_name)
        for s_idx in active_rooms[room]["seats"]:
            if active_rooms[room]["seats"][s_idx] and active_rooms[room]["seats"][s_idx].get('name') == target_name:
                active_rooms[room]["seats"][s_idx] = None
        emit('update_seats', active_rooms[room]["seats"], room=room)
        emit('chat_message', {"sender": "Sistem", "text": f"🛡️ Moderatör eylemi uygulandı: {target_name} için {action.upper()}", "type": "entrance"}, room=room)

@socketio.on('send_chat')
def handle_chat(data):
    emit('chat_message', data, room=data['room'])

@socketio.on('sync_music')
def handle_music(data):
    emit('play_music_sync', {"audioUrl": data['audioUrl'], "songName": data['songName']}, room=data['room'])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8082))
    print(f"Yoho Cloud Enterprise Sunucusu {port} portunda başlatılıyor...")
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

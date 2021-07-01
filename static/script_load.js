// カウントダウンする秒数
var sec = 4;

// 開始日時を設定
var dt = new Date();
// 終了時刻を開始日時+カウントダウンする秒数に設定
var endDt = new Date(dt.getTime() + sec * 1000);

// 1秒おきにカウントダウン
var cnt = sec;
var id = setInterval(function () {
    cnt--;
    document.getElementById('timer').innerText = cnt;
    // 現在日時と終了日時を比較
    dt = new Date();
    if (dt.getTime() >= endDt.getTime()) {
        clearInterval(id);
    }
}, 1000);


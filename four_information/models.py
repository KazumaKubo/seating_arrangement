from django.db import models


class NameManagement(models.Model):
    student_number = models.PositiveIntegerField(
        verbose_name='出席番号',
        primary_key=True,
        editable=True,
        unique=True,
        help_text='出席番号．ユニークな値であること．'
    )
    last_name = models.CharField(verbose_name='苗字', max_length=30)
    first_name = models.CharField(verbose_name='名前', max_length=30)
    rubi = models.CharField(verbose_name='ふりがな', max_length=60)
    active = models.BooleanField(
        verbose_name='有効化',
        default=1,
        help_text='席替えの有効化の設定．チェックをオフにすると席替えで配置されないので注意．'
    )

    def __str__(self):
        return str(self.student_number) + ':' + self.last_name + ' ' + self.first_name


class SeatManagement(models.Model):
    seat_number = models.PositiveIntegerField(
        verbose_name='席番号',
        primary_key=True,
        editable=True,
        unique=True,
        help_text='席番号の入力．ユニークな値であること．'
    )
    name = models.ForeignKey(
        'NameManagement',
        verbose_name='名前',
        help_text='座席の指定．シャッフルを行う前に必ず指定しておくこと．',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    lk = models.BooleanField(
        verbose_name='席のロック',
        help_text='固定する人はチェックを入れること．',
        default=0
    )
    weight = models.PositiveIntegerField(
        verbose_name='席の重み',
        help_text='シャッフルの際の席の重みをつけることにより，サーバー処理による乱数発生の偏りを解決する．',
    )

    def __str__(self):
        return str(self.seat_number)


class SeatHistory(models.Model):
    seat_number = models.ForeignKey(
        'SeatManagement',
        verbose_name='座席番号',
        help_text='座席番号．',
        on_delete=models.CASCADE
    )
    h_name = models.ForeignKey(
        'NameManagement',
        verbose_name='名前',
        editable=True,
        help_text='座席履歴．過去の座席履歴の保存．編集禁止！！！！',
        on_delete=models.CASCADE,
        null=True,
        blank=False
    )
    save_date = models.DateTimeField(
        verbose_name='実行日時',
        auto_now_add=False,
    )

    def __str__(self):
        return str(self.seat_number)


class Zone(models.Model):
    zone = models.PositiveIntegerField(
        verbose_name='ゾーンの番号．'
    )
    seat = models.ManyToManyField(
        'SeatManagement'
    )

    def __str__(self):
        return str(self.zone)
# Create your models here.

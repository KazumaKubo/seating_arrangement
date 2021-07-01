from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView
from django.db.models import Max
from django.utils import timezone

import random

from .models import SeatManagement, NameManagement, SeatHistory, Zone


class Main(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['history'] = SeatHistory.objects.filter(seat_number=1)
        context['print'] = SeatHistory.objects.filter(seat_number=1)
        return context

    template_name = 'four_information/seat_arrangement.html'


def check_seat(seat_num, student_id):
    seat_history = SeatHistory.objects.filter(seat_number__seat_number=seat_num)
    name = []
    for data in seat_history:
        name.append(data.h_name.student_number)
    if student_id in name:
        return 0
    else:
        return seat_num


def random_choice(student_id, seat_result):
    zone_num = []

    zone_count = Zone.objects.all().aggregate(Max('zone'))
    zone_max = zone_count['zone__max']

    while True:
        if Zone.objects.filter(zone=zone_max).exists():
            seat_count = Zone.objects.get(zone=zone_max).seat.count()
            seats = Zone.objects.get(zone=zone_max).seat.all()
            if seat_count == 0:
                continue
            for data in seats:
                zone_num.append(data.seat_number)
            while len(zone_num) != 0:
                seat_random = random.choice(zone_num)
                zone_num.remove(seat_random)
                result = check_seat(seat_random, student_id)
                if result == 0:
                    continue
                elif result in seat_result:
                    continue
                else:
                    return result
            zone_max -= 1
        else:
            zone_max -= 1
        if zone_max == 0:
            break

    return 0


def seat_save(result):
    for i in result.keys():
        obj = SeatManagement(
            seat_number=result[i],
            name_id=i,
            lk=SeatManagement.objects.get(seat_number=result[i]).lk,
            weight=SeatManagement.objects.get(seat_number=result[i]).weight
        )
        obj.save()


nmo = 0


@login_required(login_url='/accounts/login')
def save_seat_history(request):
    result_model = SeatManagement.objects.all()
    for data in result_model:
        SeatHistory.objects.create(
            seat_number_id=data.seat_number,
            h_name_id=data.name.student_number,
            save_date=timezone.now()
        )
    return redirect('Main')


@login_required(login_url='/accounts/login')
def seat_arrange(request):
    """
        この関数は席替えアルゴリズムに乗っ取って席替えを行う処理である．
        1．座席数と指定席の確認のためSeatManagementへアクセス．
        2．SeatManagementの席番号をKey，人をValueとして辞書へ格納．
        3．NameManagementから出席番号をKey,Valueを0で保存する．
        4．SeatHistoryへ出席番号で検索をかけ，辞書へ保存する．
        5．SeatManagementへ4の辞書の値をもとに検索を行い，席のweightを確認する．
        6．3の辞書へValue+weightの値を計算しValueの値を更新する．
        7．指定された月分計算を繰り返す．(Default=3Month)
        8．3の辞書をValueの大きい順でソートする．
        9．Zone7→Zone6→Zone5→･･･→Zone1の順で上からランダムを行う．
           乱数の値の範囲の席がヒットしなかったら次のZoneの乱数へ移動．
        10．乱数で席の指定が成功したら以前にその席になったことがないかの確認を行う．
           SeatHistoryへ座席&出席番号で検索．
           ヒット0件ならSeatManagementへ保存．
        11．全員の指定が終了し次第結果表示画面へ遷移．
        """
    global nmo
    sm = SeatManagement.objects.all().count()  # 席の数の確認
    member = NameManagement.objects.filter(active=1).count()  # 席替えの人数の確認
    # 席数と学生数が一致するかの確認．一致しない場合警告を表示．一致する場合は席数と人数の情報表示．
    if sm != member:
        context = {
            'txt': '座席の数と席替えの人数が一致しません．このままでは抽選不可能な人がいるかもしれません．'
        }
    else:
        context = {
            'seat': sm,
            'num': member
        }

        seat_name = {}  # もろもろの宣言．辞書の用意．
        name = {}
        seat_history = {}
        result = {}
        seat_result = []

        # 辞書seat_nameにKey:座席番号,Value:名前を格納する
        # 辞書nameにKey:出席番号，Value:初期化値0で初期化する
        # 辞書seat_historyにKey:出席番号，Value:席番号で初期化する
        # 辞書nameに席の重み等々を計算した値を格納しなおす
        member = NameManagement.objects.all().count()
        for i in range(member):
            if SeatManagement.objects.filter(seat_number=i + 1).exists():
                smo = SeatManagement.objects.get(seat_number=i + 1)
                seat_name[smo.seat_number] = smo.name

            if NameManagement.objects.filter(student_number=i + 1, active=1).exists():
                nmo = NameManagement.objects.get(student_number=i + 1, active=1)
                name[nmo.student_number] = 0

            for j in range(1, 13):
                sho = SeatHistory.objects.filter(h_name__student_number=i + 1, save_date__month=str(j)).exists()
                if sho:
                    sho = SeatHistory.objects.get(h_name__student_number=i + 1, save_date__month=str(j))
                    seat_history[nmo.student_number] = sho.seat_number.seat_number
                    smg = SeatManagement.objects.get(seat_number=sho.seat_number.seat_number)
                    name[nmo.student_number] += smg.weight
                else:
                    continue

        member = NameManagement.objects.filter(active=1).count()
        for i in range(member):
            if SeatManagement.objects.filter(seat_number=i + 1).exists():
                smo = SeatManagement.objects.get(seat_number=i + 1)
                if smo.lk == 1:
                    result[smo.name.student_number] = smo.seat_number
            else:
                continue

        smo = SeatManagement.objects.filter(lk=1)

        for data in smo:
            seat_result.append(data.seat_number)

        # nameをValueの大きい順に並べ変える
        # nameに格納しなおす
        name_reverse = sorted(name.items(), reverse=True, key=lambda x: x[1])
        name.clear()

        for i in range(0, len(name_reverse)):
            name[name_reverse[i][0]] = name_reverse[i][1]

        name_weight_max = max(name.values())

        name_weight = []
        student_number = []

        for i in name.keys():
            if i in result:
                continue
            else:
                student_number.append(i)
                name_weight.append(name[i])

        i = 0

        while True:
            same_number_count = name_weight.count(name_weight_max)
            name_p_same = []
            if same_number_count == 0:
                name_weight_max -= 1
                continue
            else:
                for j in range(same_number_count):
                    name_p_same.append(student_number[i])
                    i += 1

                while len(name_p_same) > 0:
                    random_name = random.choice(name_p_same)
                    name_p_same.remove(random_name)

                    seat = random_choice(random_name, seat_result)
                    seat_result.append(seat)
                    result[random_name] = seat

                name_weight_max -= 1

            if len(seat_result) == SeatManagement.objects.all().count():
                seat_save(result)
                break

    return render(request, 'four_information/load.html', context)


class SeatHistoryView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login/'
    model = SeatHistory

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = SeatHistory.objects.filter(save_date__month=self.kwargs['pk'] + 1)
        context['date'] = self.kwargs['pk'] + 1
        context['print'] = self.kwargs['pk']
        return context

    template_name = 'four_information/history.html'


class DisplaySeat(LoginRequiredMixin, ListView):
    login_url = '/accounts/login/'
    model = SeatManagement

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = timezone.now()
        return context

    template_name = 'four_information/result.html'


class PrintSeat(LoginRequiredMixin, ListView):
    login_url = '/accounts/login/'
    template_name = 'four_information/print.html'
    model = SeatHistory

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = SeatHistory.objects.filter(save_date__month=self.kwargs['pk'] + 1)
        context['date'] = self.kwargs['pk'] + 1
        return context


class DisplayPrioritySeat(LoginRequiredMixin, ListView):
    login_url = '/accounts/login'
    template_name = 'four_information/priority.html'
    model = Zone
    count = SeatManagement.objects.count()
    zone_num = {}
    column = []
    for i in range(1, count + 1):
        column.append({SeatManagement.objects.get(seat_number=i).weight: Zone.objects.get(seat__seat_number=i).zone})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = self.zone_num
        context['column_list'] = self.column
        return context


def create_score():
    global nmo
    member = NameManagement.objects.all().count()
    name = {}

    for i in range(member):

        if NameManagement.objects.filter(student_number=i + 1, active=1).exists():
            nmo = NameManagement.objects.get(student_number=i + 1, active=1)
            name[nmo.student_number] = 0

        for j in range(1, 13):
            sho = SeatHistory.objects.filter(h_name__student_number=i + 1, save_date__month=str(j)).exists()
            if sho:
                sho = SeatHistory.objects.get(h_name__student_number=i + 1, save_date__month=str(j))
                smg = SeatManagement.objects.get(seat_number=sho.seat_number.seat_number)
                name[nmo.student_number] += smg.weight
            else:
                continue

    name_list = {}
    for i in name:
        sno = NameManagement.objects.get(student_number=i)
        name_obj = str(sno.student_number) + '. ' + str(sno.last_name) + ' ' + str(sno.first_name)
        name_list[name_obj] = name[i]
    return name_list


class DisplayStudentWeight(LoginRequiredMixin, ListView):
    login_url = '/accounts/login'
    template_name = 'four_information/weight.html'
    model = NameManagement

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = create_score()

        return context
# Create your views here.

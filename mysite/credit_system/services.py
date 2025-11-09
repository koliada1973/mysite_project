from decimal import Decimal
from datetime import date, datetime

from credit_system.models import Credit


def process_payment(credit: Credit, pay, date_pay, delta_days) -> dict:
    """
    Розраховує нараховані відсотки, борг, оновлює залишок і дату останнього платежу.
    Повертає словник з результатами.
    """

    daily_percent = credit.percent / 100
    dolg_percent = round(credit.dolg_percent, 2)
    ostatok = round(credit.ostatok, 2)

    summa_percent = 0
    pog_summa_percent = 0
    new_dolg_percent = 0
    pog_credit = 0
    ost_payment = 0



    if delta_days < 0:
        raise ValueError("Дата платежу не може бути раніше останньої дати платежу.")

    # daily_rate = credit.percent / Decimal(100)
    summa_percent = round(ostatok * daily_percent * delta_days, 2)

    # Загальна заборгованість по відсотках
    total_summa = round(dolg_percent + summa_percent, 2)
    ost_payment = pay

    # log = []  # для пояснення, що відбулося

    # Платіж менший, ніж відсотки
    if ost_payment < total_summa:
        new_dolg_percent = round(total_summa - ost_payment, 2)
        if ost_payment <= dolg_percent:
            pog_summa_percent = 0
        else:
            pog_summa_percent = round(ost_payment - total_summa, 2)
        credit.dolg_percent = new_dolg_percent
        # log.append(f"Платіж {pay:.2f} грн покрив лише частину відсотків.")
        # log.append(f"Новий борг по відсотках: {credit.dolg_percent:.2f} грн.")

    else:
        # 1. Гасимо борг по відсотках
        ost_payment -= credit.dolg_percent
        new_dolg_percent = 0
        credit.dolg_percent = new_dolg_percent


        # 2. Гасимо нараховані відсотки
        if ost_payment <= summa_percent:
            pog_summa_percent = round(summa_percent - ost_payment, 2)
            ost_payment = 0
        else:
            ost_payment -= summa_percent
            pog_summa_percent = summa_percent

        # 3. Якщо залишилось — гасимо тіло кредиту
        if ost_payment > 0:
            if ost_payment >= credit.ostatok:
                pog_credit = credit.ostatok
                ost_payment -= pog_credit
                ostatok = 0
                credit.ostatok = ostatok
                credit.closed = True
                # log.append("Кредит повністю погашено.")
            else:
                pog_credit = ost_payment
                ostatok-= pog_credit
                credit.ostatok = ostatok
                ost_payment = 0
                # log.append(f"Погашено частину кредиту на {ost_payment:.2f} грн.")


    # Оновлюємо дату останнього платежу
    credit.last_pay_date = date_pay
    credit.save()


    result = {
        # "days": delta_days,
        "summa_percent": summa_percent,
        "pog_summa_percent":pog_summa_percent,
        "dolg_percent":new_dolg_percent,
        "pog_credit": pog_credit,
        "ostatok": credit.ostatok,
        "ost_payment": ost_payment,
        # "log": log,
    }

    return result
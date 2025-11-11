from datetime import datetime, date
import calendar


def to_cents(x: float) -> int:
    """Перетворення у копійки"""
    return int(round(x * 100))

def from_cents(x: int) -> float:
    """Назад у гривні."""
    return x / 100.0


def rozrahunok_payment(credit_sum, daily_rate, months, start_date, pay_day, pay):
    """Повертає фінальний залишок (тіло + борг по відсотках) у копійках."""
    if isinstance(start_date, str):
        # Використовуємо strptime
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    current_date = start_date

    ostatok = to_cents(credit_sum)
    dolg_by_percents = 0

    for m in range(1, months + 1):
        # Дата наступного платежу
        year, month = current_date.year, current_date.month
        month += 1
        if month > 12:
            month = 1
            year += 1
        last_day = calendar.monthrange(year, month)[1]
        date_pay = date(year, month, min(pay_day, last_day))

        # Нараховані відсотки
        days = (date_pay - current_date).days
        percents = to_cents(from_cents(ostatok) * daily_rate * days)

        ost_payment = pay

        # 1. Погашення боргу по %
        if ost_payment >= dolg_by_percents:
            ost_payment -= dolg_by_percents
            dolg_by_percents = 0
        else:
            dolg_by_percents -= ost_payment
            ost_payment = 0

        # 2. Погашення поточних %
        if ost_payment >= percents:
            ost_payment -= percents
        else:
            dolg_by_percents += (percents - ost_payment)
            ost_payment = 0

        # 3. Погашення тіла
        ostatok -= ost_payment

        current_date = date_pay

    return ostatok + dolg_by_percents


def rozrahunok_plan_pay(credit_sum, daily_percent, months, start_date, pay_day, tol=1, max_iter=200):
    """
    Підбирає платіж так, щоб фінальний баланс був <= 0.
    """

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()


    low, high = 0, to_cents(credit_sum) * 2
    pay = (low + high) // 2

    for _ in range(max_iter):
        final_ostatok = rozrahunok_payment(credit_sum, daily_percent, months, start_date, pay_day, pay)

        if -tol <= final_ostatok <= tol:
            break
        if final_ostatok > 0:  # Якщо залишок > 0 што платіж малий
            low = pay
        else:  # Якщо залишок < 0 то платіж завеликий
            high = pay

        pay = (low + high) // 2

    # Гарантуємо, що борг погашений (залишок ≤ 0)
    final_ostatok = rozrahunok_payment(credit_sum, daily_percent, months, start_date, pay_day, pay)

    # Якщо при розрахованому платежі кінцевий залишок більше нулю - додаємо 1 копійку
    if final_ostatok > 0:
        pay += 1

    # Фінальний графік
    grafik = []
    current_date = start_date
    ostatok = to_cents(credit_sum)
    dolg_by_percents = 0
    total_pays_sum = 0

    for m in range(1, months + 1):
        year, month = current_date.year, current_date.month
        month += 1
        if month > 12:
            month = 1
            year += 1
        last_day = calendar.monthrange(year, month)[1]
        date_pay = date(year, month, min(pay_day, last_day))

        days = (date_pay - current_date).days
        percents = to_cents(from_cents(ostatok) * daily_percent * days)
        ost_payment = pay

        # 1. Погашення боргу по %
        if ost_payment >= dolg_by_percents:
            pog_dolg_by_percents = dolg_by_percents
            ost_payment -= dolg_by_percents
            dolg_by_percents = 0
        else:
            pog_dolg_by_percents = ost_payment
            dolg_by_percents -= ost_payment
            ost_payment = 0

        # 2. Поточні %
        if ost_payment >= percents:
            pog_percents = percents
            ost_payment -= percents
        else:
            pog_percents = ost_payment
            dolg_by_percents += (percents - ost_payment)
            ost_payment = 0

        # 3. Тіло
        pog_ostatok = ost_payment
        ostatok -= pog_ostatok
        current_pay = pay
        if ostatok < 0:
            current_pay = pay + ostatok
            ostatok = 0

        total_pays_sum += pay

        grafik.append({
            "number": m,
            "date_of_pay": date_pay.strftime("%d.%m.%Y"),   # "%Y-%m-%d"
            "delta_days": days,
            "payment": from_cents(current_pay),
            "summa_percent": from_cents(percents),
            "pog_dolg_by_percents": from_cents(pog_dolg_by_percents),
            "pog_summa_percent": from_cents(pog_percents),
            "dolg_percent": from_cents(dolg_by_percents),
            "pog_credit": from_cents(pog_ostatok),
            "ostatok": from_cents(ostatok),
            "total_dolg": from_cents(ostatok + dolg_by_percents)
        })

        current_date = date_pay

    pereplata = from_cents(total_pays_sum) - credit_sum
    return from_cents(pay), grafik, from_cents(total_pays_sum), round(pereplata, 2)



# suma_credit = 1000
# daily_percent = 0.0010
# months = 18
# start_date = "2025-11-9"
# pay_day = 15
#
# plan_pay, grafik = rozrahunok_plan_pay(suma_credit, daily_percent, months, start_date, pay_day)
#
# print(f"Підібраний щомісячний платіж (plan_pay) ≈ {plan_pay:.2f} грн\n")
# print("Графік (grafik):")
# for row in grafik:
#     print(row)
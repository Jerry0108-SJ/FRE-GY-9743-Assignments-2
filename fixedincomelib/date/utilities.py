import pandas as pd
from typing import Optional
import QuantLib as ql
from QuantLib import Period
from fixedincomelib.date.basics import Date, Period
from fixedincomelib.market import HolidayConvention, BusinessDayConvention, AccrualBasis


def add_period(
    start_date: Date,
    term: Period,
    business_day_convention: Optional[BusinessDayConvention] = BusinessDayConvention("F"),
    holiday_convention: Optional[HolidayConvention] = HolidayConvention("USGS"),
    end_of_month: Optional[bool] = False,
):

    this_cal = holiday_convention.value
    return Date(this_cal.advance(start_date, term, business_day_convention.value, end_of_month))


def move_to_business_day(
    input_date: Date,
    business_day_convention: BusinessDayConvention,
    holiday_convention: HolidayConvention,
):
    return Date(holiday_convention.value.adjust(input_date, business_day_convention.value))


def accrued(
    start_date: Date,
    end_date: Date,
    accrual_basis: Optional[AccrualBasis] = AccrualBasis("ACT/ACT"),
    business_day_convention: Optional[BusinessDayConvention] = BusinessDayConvention("F"),
    holiday_convention: Optional[HolidayConvention] = HolidayConvention("USGS"),
    reference_period_start: Optional[Date] = None,
    reference_period_end: Optional[Date] = None,
):
    # ACT/ACT (ICMA) divides by the length of the quasi-coupon period the dates fall in,
    # so it needs that period spelled out; every other basis has a fixed denominator and
    # ignores these two arguments. Pass the quasi-coupon period that *ends* on the coupon
    # date -- QuantLib extrapolates the grid backwards from there, which is what makes a
    # long stub spanning several quasi-coupon periods come out right.
    adjusted_end_dt = move_to_business_day(end_date, business_day_convention, holiday_convention)
    if reference_period_start is not None and reference_period_end is not None:
        return accrual_basis.value.yearFraction(
            start_date, adjusted_end_dt, reference_period_start, reference_period_end)
    return accrual_basis.value.yearFraction(start_date, adjusted_end_dt)


def is_business_day(input_date: Date, holiday_convention: HolidayConvention):
    return holiday_convention.value.isBusinessDay(input_date)


def is_holiday(input_date: Date, holiday_convention: HolidayConvention):
    return holiday_convention.value.isHoliday(input_date)


def is_end_of_month(input_date: Date, holiday_convention: HolidayConvention):
    return holiday_convention.value.isEndOfMonth(input_date)


def end_of_month(input_date: Date, holiday_convention: HolidayConvention):
    return holiday_convention.value.endOfMonth(input_date)


def make_schedule(
    start_date: Date,
    end_date: Date,
    accrual_period: Period,
    holiday_convention: HolidayConvention,
    business_day_convention: BusinessDayConvention,
    accrual_basis: AccrualBasis,
    rule: Optional[str] = "BACKWARD",
    end_of_month: Optional[bool] = False,
    fix_in_arrear: Optional[bool] = False,
    fixing_offset: Optional[Period] = Period("0D"),
    payment_offset: Optional[Period] = Period("0D"),
    pay_business_day_convention: Optional[BusinessDayConvention] = BusinessDayConvention("F"),
    pay_holiday_convention: Optional[HolidayConvention] = HolidayConvention("USGS"),
    first_regular_date: Optional[Date] = None,
    last_regular_date: Optional[Date] = None,
    first_accrual_basis: Optional[AccrualBasis] = None,
    last_accrual_basis: Optional[AccrualBasis] = None,
) -> pd.DataFrame:

    if rule.upper() not in ('BACKWARD', 'FORWARD'):
        raise ValueError('rule must be BACKWARD or FORWARD')
    this_rule = (
        ql.DateGeneration.Backward if rule.upper() == "BACKWARD" else ql.DateGeneration.Forward
    )
    this_first_date = first_regular_date if first_regular_date is not None else ql.Date()

    # set up start date and end date of each period
    this_schedule = ql.Schedule(
        start_date,
        end_date,
        accrual_period,
        holiday_convention.value,
        business_day_convention.value,
        business_day_convention.value,
        this_rule,
        end_of_month,
        this_first_date,
        last_regular_date if last_regular_date is not None else ql.Date(),
    )

    # add fixing date and payment date
    start_dates = this_schedule.dates()[:-1]
    end_dates = this_schedule.dates()[1:]
    fixing_dates, payment_dates, accs = [], [], []
    ref_starts, ref_ends, regular_flags = [], [], []
    for i, (s, e) in enumerate(zip(start_dates, end_dates)):
        regular = this_schedule.isRegular(i + 1) or e == add_period(
            Date(s), accrual_period, BusinessDayConvention('NONE'),
            HolidayConvention('NONE'), end_of_month)
        ref_start, ref_end = s, e
        if not regular:
            # First stubs reference the grid ending at the first coupon;
            # final stubs reference the grid starting at the last regular coupon.
            if i == 0 and (len(start_dates) > 1 or rule.upper() == 'BACKWARD'):
                ref_start = add_period(Date(e), Period(-accrual_period.length(), accrual_period.units()),
                                       BusinessDayConvention('NONE'), HolidayConvention('NONE'), end_of_month)
            elif i == len(start_dates) - 1:
                ref_end = add_period(Date(s), accrual_period,
                                     BusinessDayConvention('NONE'), HolidayConvention('NONE'), end_of_month)
            else:
                raise ValueError('Only first and last coupon periods may be irregular')
        basis = accrual_basis
        if i == 0 and first_accrual_basis is not None:
            basis = first_accrual_basis
        elif i == len(start_dates) - 1 and last_accrual_basis is not None:
            basis = last_accrual_basis
        f = s
        if fixing_offset != "":
            f = add_period(
                e if fix_in_arrear else s,
                fixing_offset,
                business_day_convention,
                holiday_convention,
            )
        fixing_dates.append(f)
        p = e
        if payment_offset != "":
            p = add_period(
                e, payment_offset, pay_business_day_convention, pay_holiday_convention
            )
        payment_dates.append(p)
        accs.append(accrued(s, e, basis, business_day_convention, holiday_convention,
                           ref_start if basis.needs_reference_period else None,
                           ref_end if basis.needs_reference_period else None))
        ref_starts.append(ref_start)
        ref_ends.append(ref_end)
        regular_flags.append(regular)

    # set up container
    df = pd.DataFrame(columns=["StartDate", "EndDate", "FixingDate", "PaymentDate", "Accrued"])
    df["StartDate"] = start_dates
    df["EndDate"] = end_dates
    df["FixingDate"] = fixing_dates
    df["PaymentDate"] = payment_dates
    df["Accrued"] = accs
    df['ReferenceStart'] = ref_starts
    df['ReferenceEnd'] = ref_ends
    df['IsRegular'] = regular_flags

    return df


def frequency_from_period(p: str) -> float:
    freq = p.frequency()
    return float(freq)

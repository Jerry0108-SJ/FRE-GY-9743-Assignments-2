import pandas as pd
from typing import Optional
from fixedincomelib.date import *
from fixedincomelib.market.basics import (
    AccrualBasis, BusinessDayConvention, HolidayConvention)

def qfAddPeriod(start_date : str, term : str, business_day_convention : Optional[str]='NONE', holiday_convention : Optional[str]='NONE', end_of_month : Optional[bool]=False):
    this_date = add_period(
        Date(start_date),
        Period(term), 
        BusinessDayConvention(business_day_convention), 
        HolidayConvention(holiday_convention), 
        end_of_month)
    return this_date.ISO()

def qfAccrued(start_date : str, end_date : str, accrual_basis : Optional[str]='NONE', business_day_convention : Optional[str]='NONE', holiday_convention : Optional[str]='NONE', reference_period_start : Optional[str]=None, reference_period_end : Optional[str]=None):
    return accrued(
        Date(start_date),
        Date(end_date),
        AccrualBasis(accrual_basis),
        BusinessDayConvention(business_day_convention),
        HolidayConvention(holiday_convention),
        Date(reference_period_start) if reference_period_start else None,
        Date(reference_period_end) if reference_period_end else None)

def qfMoveToBusinessDay(input_date : str, business_day_convention : str, holiday_convention : str):
    moved_date = move_to_business_day(
        Date(input_date), 
        BusinessDayConvention(business_day_convention), 
        HolidayConvention(holiday_convention))
    return moved_date.ISO()

def qfIsBusinessDay(input_date : str, holiday_convention : str):
    return is_business_day(Date(input_date), HolidayConvention(holiday_convention))

def qfIsHoliday(input_date : str, holiday_convention : str):
    return is_holiday(Date(input_date), HolidayConvention(holiday_convention))

def qfIsEndOfMonth(input_date : str, holiday_convention : str):
    return is_end_of_month(Date(input_date), HolidayConvention(holiday_convention))

def qfEndOfMonth(input_date : str, hol_conv : str):
    this_date = end_of_month(Date(input_date), HolidayConvention(hol_conv))
    return this_date.ISO()

def qfCreateSchedule(
        start_date : str, 
        end_date : str, 
        accrual_period : str,
        holiday_convention : str,
        business_day_convention : str, 
        accrual_basis : str,
        rule : Optional[str]='BACKWARD', 
        end_of_month : Optional[bool]=False,
        fix_in_arrear : Optional[bool]=False, 
        fixing_offset : Optional[str]='0D',
        payment_offset : Optional[str]='0D',
        pay_business_day_convention : Optional[str]='F',
        pay_holiday_convention : Optional[str]='USGS',
        first_regular_date : Optional[str]=None,
        last_regular_date : Optional[str]=None,
        first_accrual_basis : Optional[str]=None,
        last_accrual_basis : Optional[str]=None) -> pd.DataFrame:
    """Return coupon periods and year fractions (Accrued is not a cash amount).

    Specify first/last regular dates to anchor irregular coupons. For ICMA,
    reference periods are supplied to the day counter, including long stubs.
    Interest = face * annual coupon rate * Accrued for the supplied bond cases.
    """

    return make_schedule(
        Date(start_date),
        Date(end_date),
        Period(accrual_period),
        HolidayConvention(holiday_convention),
        BusinessDayConvention(business_day_convention),
        AccrualBasis(accrual_basis),
        rule,
        end_of_month,
        fix_in_arrear,
        Period(fixing_offset),
        Period(payment_offset),
        BusinessDayConvention(pay_business_day_convention),
        HolidayConvention(pay_holiday_convention),
        Date(first_regular_date) if first_regular_date else None,
        Date(last_regular_date) if last_regular_date else None,
        AccrualBasis(first_accrual_basis) if first_accrual_basis else None,
        AccrualBasis(last_accrual_basis) if last_accrual_basis else None)

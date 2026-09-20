import pandas as pd
from typing import Optional
# in-house
from fixedincomelib.date import *
from fixedincomelib.market import *

def qfAddPeriod(
        start_date : str, 
        term : str, 
        business_day_convention : Optional[str]='NONE', 
        holiday_convention : Optional[str]='NONE', 
        end_of_month : Optional[bool]=False):
    
    this_date = add_period(
        Date(start_date),
        Period(term), 
        BusinessDayConvention.new(business_day_convention), 
        HolidayConvention.new(holiday_convention), 
        end_of_month)
    
    return Date.to_string(this_date)

def qfSubtractPeriod(
        start_date : str, 
        term : str, 
        business_day_convention : Optional[str]='NONE', 
        holiday_convention : Optional[str]='NONE', 
        end_of_month : Optional[bool]=False):
    
    this_date = subtract_period(
        Date(start_date),
        Period(term), 
        BusinessDayConvention.new(business_day_convention), 
        HolidayConvention.new(holiday_convention), 
        end_of_month)
    
    return Date.to_string(this_date)

def qfAccrued(
        start_date : str, 
        end_date : str, 
        accrual_basis : Optional[str]='NONE', 
        business_day_convention : Optional[str]='NONE', 
        holiday_convention : Optional[str]='NONE'):
    
    return accrued(
        Date(start_date), 
        Date(end_date), 
        AccrualBasis.new(accrual_basis), 
        BusinessDayConvention.new(business_day_convention), 
        HolidayConvention.new(holiday_convention))

def qfMoveToBusinessDay(
        input_date : str, 
        business_day_convention : str, 
        holiday_convention : str):
    
    moved_date = move_to_business_day(
        Date(input_date), 
        BusinessDayConvention.new(business_day_convention), 
        HolidayConvention.new(holiday_convention))
    
    return Date.to_string(moved_date)

def qfIsBusinessDay(input_date : str, holiday_convention : str):
    return is_business_day(Date(input_date), HolidayConvention.new(holiday_convention))

def qfIsHoliday(input_date : str, holiday_convention : str):
    return is_holiday(Date(input_date), HolidayConvention.new(holiday_convention))

def qfIsEndOfMonth(input_date : str, holiday_convention : str):
    return is_end_of_month(Date(input_date), HolidayConvention.new(holiday_convention))

def qfEndOfMonth(input_date : str, hol_conv : str):
    this_date = end_of_month(Date(input_date), HolidayConvention.new(hol_conv))
    return Date.to_string(this_date)

def qfCreateSchedule(
        start_date : str, 
        end_date : str, 
        accrual_period : str,
        holiday_convention : str,
        business_day_convention : str, 
        accrual_basis : str,
        rule : Optional[int]=ql.DateGeneration.Backward, 
        end_of_month : Optional[bool]=False,
        fix_in_arrear : Optional[bool]=False, 
        fixing_offset : Optional[str]='0D',
        payment_offset : Optional[str]='0D',
        payment_offset_business_day_convention : Optional[str]='F',
        payment_offset_holiday_convention: Optional[str]='USGS',
        first_regular_date : Optional[str]='',
        next_to_last_date : Optional[str]='',
        pay_in_advance : Optional[bool]=False) -> pd.DataFrame:

    assert rule.upper() in ['BACKWARD', 'FORWARD']
    this_rule = ql.DateGeneration.Backward
    if rule.upper() == 'FORWARD':
            this_rule = ql.DateGeneration.Forward

    return make_schedule(
        Date(start_date),
        Date(end_date),
        Period(accrual_period),
        HolidayConvention.new(holiday_convention),
        BusinessDayConvention.new(business_day_convention),
        AccrualBasis.new(accrual_basis),
        this_rule,
        end_of_month,
        fix_in_arrear,
        Period(fixing_offset),
        pay_in_advance,
        Period(payment_offset),
        BusinessDayConvention.new(payment_offset_business_day_convention),
        HolidayConvention.new(payment_offset_holiday_convention),
        Date(first_regular_date),
        Date(next_to_last_date),
        True)
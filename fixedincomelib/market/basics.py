from typing import Optional
import QuantLib as ql

### below are some wrappers to allow str -> quantlib object conversion
### currency, businessdayconvention, holidayconvention, accrualbasis

class Currency:

    def __init__(self, input : str) -> None:

        self.ccy = None
        self.is_valid_ = True
        if input.upper() == 'USD':
            self.ccy = ql.USDCurrency()
        elif input.upper() == 'CAD':
            self.ccy = ql.CADCurrency()
        elif input.upper() == 'GBP':
            self.ccy = ql.GBPCurrency()
        elif input.upper() == 'EUR':
            self.ccy = ql.EURCurrency()
        elif input.upper() == 'JPY':
            self.ccy = ql.JPYCurrency()
        elif input.upper() == 'AUD':
            self.ccy = ql.AUDCurrency()
        else:
            self.ccy = None
            self.is_valid_ = False
            
    def __eq__(self, other):
        return isinstance(other, Currency) and self.ccy.code() == other.ccy.code()

    def __hash__(self):
        return hash(self.ccy.code())

    @property
    def value(self):
        return self.ccy
    
    @property
    def value_str(self):
        return self.ccy.code()

    def code(self):
        return self.ccy.code()

    @property
    def is_valid(self):
        return self.is_valid_

class BusinessDayConvention:
    
    def __init__(self, input : Optional[str]='NONE') -> None:
        self.value_str_ = input
        self.value_ = None
        if self.value_str_.upper() == 'MF':
            self.value_ = ql.ModifiedFollowing
        elif self.value_str_.upper() == 'F':
            self.value_ = ql.Following
        elif self.value_str_.upper() == 'P':
            self.value_ = ql.Preceding
        elif self.value_str_.upper() == 'NONE':
            self.value_ = ql.Unadjusted
        else:
            raise Exception(self.value_str_ + ' is not current supported business day convention.')

    @property
    def value(self):
        return self.value_
    
    @property
    def value_str(self):
        return self.value_str_
    
class HolidayConvention:
    
    def __init__(self, input : Optional[str]='NONE') -> None:
        self.value_str_ = input
        self.value_ = ql.NullCalendar()
        if self.value_str_.upper() == 'NYC':
            self.value_ = ql.UnitedStates(ql.UnitedStates.LiborImpact)
        elif self.value_str_.upper() == 'USGS':
            self.value_ = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
        elif self.value_str_.upper() == 'LON':
            self.value_ = ql.UnitedKingdom(ql.UnitedKingdom.Exchange)
        elif self.value_str_.upper() == 'TOK':
            self.value_ = ql.Japan()
        elif self.value_str_.upper() == 'TARGET':
            self.value_ = ql.JointCalendar(ql.TARGET(), ql.France(), ql.Germany(), ql.Italy()) # good enough ?
        elif self.value_str_.upper() == 'SYD':
            self.value_ = ql.Australia() 
        if self.value_ == None:
            raise Exception(self.value_str_ + ' is not current supported Hoiday Center.')

    @property
    def value(self):
        return self.value_
    
    @property
    def value_str(self):
        return self.value_str_

class AccrualBasis(ql.DayCounter):

    def __init__(self, input : Optional[str]='NONE') -> None:
        self.value_ = None
        self.value_str_ = input
        ### most bases answer "how long is this period" on their own; ACT/ACT (ICMA)
        ### is the exception -- see the note below and needs_reference_period
        self.needs_reference_period_ = False
        if self.value_str_.upper() == 'NONE':
            self.value_ = ql.SimpleDayCounter()
        elif self.value_str_.upper() in ('ACT/ACT', 'ACT/ACT (ISDA)', 'ACTUAL/ACTUAL (ISDA)'):
            self.value_ = ql.ActualActual(ql.ActualActual.ISDA)
        elif self.value_str_.upper() in (
            'ACT/ACT (ISMA)', 'ACTUAL/ACTUAL (ISMA)',
            'ACT/ACT (ICMA)', 'ACTUAL/ACTUAL (ICMA)'):
            ### ICMA (formerly ISMA) measures a period against the coupon schedule: the
            ### denominator is the number of days in the quasi-coupon period the dates
            ### fall in, not a constant. Callers must therefore hand yearFraction the
            ### reference period; without it QuantLib assumes the dates span a regular
            ### period and silently returns a simplified answer.
            self.value_ = ql.ActualActual(ql.ActualActual.ISMA)
            self.needs_reference_period_ = True
        elif self.value_str_.upper() in (
            'ACT/365 FIXED', 'ACT/365 (FIXED)', 'ACT/365',
            'ACTUAL/365 (FIXED)', 'ACTUAL/365'):
            self.value_ = ql.Actual365Fixed()
        elif self.value_str_.upper() in ('ACT/360', 'ACTUAL/360'):
            self.value_ = ql.Actual360()
        elif self.value_str_.upper() in ('30/360', 'THIRTY/360', '30/360 (BOND BASIS)', 'ISMA-30/360'):
            self.value_ = ql.Thirty360(ql.Thirty360.BondBasis)
        elif self.value_str_.upper() == '30E/360':
            self.value_ = ql.Thirty360(ql.Thirty360.European)
        elif self.value_str_.upper() == '30/360 (ISDA)':
            self.value_ = ql.Thirty360(ql.Thirty360.ISDA)
        elif self.value_str_.upper() == 'BUSINESS252':
            self.value_ = ql.Business252()
        else:
            raise Exception(self.value_str_ + ' is not current supported accrual basis.')

    @property
    def value(self):
        return self.value_

    @property
    def value_str(self):
        return self.value_str_

    @property
    def needs_reference_period(self) -> bool:
        ### True when yearFraction is only well defined once the quasi-coupon period is
        ### known, i.e. ACT/ACT (ICMA). Bases with a fixed denominator return False.
        return self.needs_reference_period_

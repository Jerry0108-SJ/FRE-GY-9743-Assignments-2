import sys
import datetime as dt
from typing import Union, Self
import QuantLib as ql


class Date(ql.Date):

    ### Extend QuantLib Date Class
    ### 1) args = iso str, e.g., 2025-05-25
    ### 2) args = datetime object, e.g., dt.datetime(2025, 5, 25)
    
    def __init__(self, *args) -> Self:
        these_args = args
        if len(these_args) == 1:
            this_arg = these_args[0]
            if this_arg == "null date" or not this_arg:
                super().__init__()
                return
            if isinstance(this_arg, ql.Date):
                # constructing directly off the serial number is a plain integer copy; going via
                # (day, month, year) instead makes QuantLib re-derive the serial number from the
                # Gregorian calendar on every call, which is measurably more expensive and entirely
                # unnecessary since this_arg is already a valid ql.Date.
                these_args = (this_arg.serialNumber(),)
            elif isinstance(this_arg, str):
                tokenized = this_arg.split('-')
                these_args = (int(tokenized[2]), int(tokenized[1]), int(tokenized[0]))
            elif isinstance(this_arg, dt.date):
                these_args = (this_arg.day, this_arg.month, this_arg.year)
        super().__init__(*these_args)

    def is_valid(self):
        return self.serialNumber() != 0

    @classmethod
    def to_string(cls, dt : "Date") -> str:
        if sys.version_info >= (3, 12):
            return dt.ISO()
        else:
            return dt.to_date().strftime('%Y-%m-%d')
        
class Period(ql.Period):
    
    def is_valid(self) -> bool:
        return self.frequency() != -1

    @classmethod
    def to_string(cls, period : ql.Period) -> str:
        return period.__str__()
    
    @classmethod
    def negate_period(cls, period : "Period") -> "Period":
        return cls('-' + Period.to_string(period))

class TermOrDate:
    
    ### Instanitate either a term object (Period) or a date object (Date)
    def __init__(self, input : Union[str, ql.Period, ql.Date]) -> Self:
        self.this_date_ = None
        self.this_term_ = None
        if isinstance(input, str):
            # it must be in iso-format
            if '-' in input:
                self.this_date_ = Date(input)
            else:
                self.this_term_ = Period(ql.NoFrequency if input == '' else input)
        elif isinstance(input, (ql.Period, Period)):
            self.this_term_ = input
        elif isinstance(input, (ql.Date, Date)):
            self.this_date_ = input

    def is_term(self) -> bool:
        return self.this_date_ == None
    
    def get_date(self) -> Date:
        return self.this_date_
    
    def get_term(self) -> Period:
        return self.this_term_
    
    @classmethod
    def to_string(cls, term_or_termination_date : "TermOrDate") -> str:
        if term_or_termination_date.is_term():
            return Period.to_string(term_or_termination_date.get_term())
        else:
            return Date.to_string(term_or_termination_date.get_date())
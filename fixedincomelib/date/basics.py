import datetime as dt
from typing import Union
import QuantLib as ql

class Date(ql.Date):

    ### Extend QunatLib Date Class
    ### 1) args = iso str, e.g., 2025-05-25
    ### 2) args = datetime object, e.g., dt.datetime(2025, 5, 25)
    
    def __init__(self, *args) -> None:
        these_args = args
        if len(these_args) == 1:
            this_arg = these_args[0]
            if isinstance(this_arg, ql.Date):
                these_args = (this_arg.dayOfMonth(), this_arg.month(), this_arg.year())
            elif isinstance(this_arg, str):
                iso = this_arg.split()[0]
                these_args = (iso, '%Y-%m-%d')
            elif isinstance(this_arg, dt.date):
                these_args = (this_arg.day, this_arg.month, this_arg.year)
        super().__init__(*these_args)


class Period(ql.Period):
    ### Just rename the class
    pass

class TermOrTerminationDate:
    
    ### Instanitate either a term object (Period) or a date object (Date)
    def __init__(self, input : Union[str, ql.Period, ql.Date]) -> None:
        self.this_date = None
        self.this_term = None
        if isinstance(input, str):
            # it must be in iso-format
            if '-' in input:
                self.this_date = Date(input)
            else:
                self.this_term = Period(input)
        elif isinstance(input, (ql.Period, Period)):
            self.this_term = input
        elif isinstance(input, (ql.Date, Date)):
            self.this_date = input

    def is_term(self) -> bool:
        return self.this_date == None
    
    def get_date(self) -> Date:
        return self.this_date
    
    def get_term(self) -> Period:
        return self.this_term
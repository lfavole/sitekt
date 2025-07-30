from common.pdfs.list import List
from common.pdfs.meetings import Meetings
from common.pdfs.quick_list import QuickList

list = List.as_view("aumonerie")
quick_list = QuickList.as_view("aumonerie")
meetings = Meetings.as_view("aumonerie")

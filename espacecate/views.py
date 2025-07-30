from common.pdfs.list import List
from common.pdfs.meetings import Meetings
from common.pdfs.quick_list import QuickList

list = List.as_view("espacecate")
quick_list = QuickList.as_view("espacecate")
meetings = Meetings.as_view("espacecate")

import os

print(os.path.isfile('/var/ossec/queue/diff/local/home/kuthoong248/Thesis/tonight/last-entry'))

# lines = ['DIRECTORY="/var/ossec"\n', 'VERSION="v2.9.1"\n', 'DATE="Fri Sep 15 23:03:39 ICT 2017"\n', 'TYPE="server"\n']
# res = {}
# for line in lines:
#     key, value = line.strip().split('=')
#     res[key] = value.strip('"')

# print(res)

# num_pages_per_side = 10     # num pages in the left or right
# num_pages = 5000         # length of value
# curr_page_num = 11

# closest_curr_page = [x for x in range(
#     curr_page_num - 2, curr_page_num + 3) if x >= 0]
# default_left_value = list(range(1, num_pages_per_side + 1))
# default_right_value = list(range(
#     num_pages - num_pages_per_side, num_pages + 1))

# if curr_page_num <= num_pages // 2:
#     left_value = []
#     if closest_curr_page[-1] > num_pages_per_side:
#         left_value = list(range(1, len(closest_curr_page) + 1))
#         left_value += closest_curr_page
#     else:
#         left_value = default_left_value
#     new_value = left_value + ['skip'] + default_right_value
# else:
#     right_value = []
#     if closest_curr_page[0] >= (num_pages - num_pages_per_side):
#         right_value = default_right_value
#     else:
#         right_value = closest_curr_page
#         right_value += list(range(
#             num_pages - len(closest_curr_page), num_pages + 1))
#     new_value = default_left_value + ['skip'] + right_value

# import pyinotify
#
# wm = pyinotify.WatchManager()  # Watch Manager
# events = pyinotify.IN_CLOSE_WRITE  # watched events
#
#
# class EventHandler(pyinotify.ProcessEvent):
#     def process_IN_CLOSE_WRITE(self, event):
#         print("CLOSE_WRITE event:", event.pathname)
#
# handler = EventHandler()
# notifier = pyinotify.Notifier(wm, handler)
# wdd = wm.add_watch('/var/ossec/queue/syscheck', events, rec=True)
#
# notifier.loop()

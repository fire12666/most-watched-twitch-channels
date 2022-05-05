from os import read
from datetime import timedelta
from channel_list import *
import csv


DATA_FILE = 'data.csv'
TOTAL_DAYS = (UNIVERSAL_LAST_DATE - UNIVERSAL_FIRST_DATE).days


def prepare_data():
    data = {}
    data["Channel"] = ["Channel"]
    data["Language"] = ["Language"]

    day = 0
    while day <= TOTAL_DAYS:
        date = str(UNIVERSAL_FIRST_DATE + timedelta(day))
        data[date] = [date]
        day += 1

    return data


def find_between(s, first, last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


def read_text_files(list, data):
    for channel in list:
        data["Channel"].append(channel.name)
        data["Language"].append(channel.language)
        text_file = open("polylines/" + channel.name)
        raw_path = find_between(text_file.read(), 'd="', '"')
        x_list, y_list = get_coords_lists(raw_path)

        days = get_days(channel, x_list)
        hours = get_hours(channel, y_list)

        current_day = 0
        index = 0

        while current_day <= TOTAL_DAYS:
            date = UNIVERSAL_FIRST_DATE + timedelta(current_day)
            if index < len(days) and date == days[index]:
                data[str(days[index])].append(hours[index])
                index = index + 1
            elif index == 0:
                data[str(date)].append(0)
            else:
                data[str(date)].append(hours[index - 1])
            current_day = current_day + 1        


def get_coords_lists(raw_path):
    coords = raw_path.replace("M", "L").split("L ")
    x_list = []
    y_list = []

    for coord in coords:
        if len(coord) > 0:
            coord_pair = coord.split(" ")
            x = coord_pair[0]
            y = coord_pair[1]

            x_list.append(x)
            y_list.append(y)

    return x_list, y_list


def get_days(channel, x_list):
    days = []
    min_x = float(x_list[0])
    max_x = float(x_list[len(x_list) - 1])

    for x in x_list:
            total_channel_days = (channel.end_date - channel.begin_date).days
            day = (float(x) - min_x) / (max_x - min_x) * total_channel_days
            days.append(channel.begin_date + timedelta(round(day)))
    return days


def get_hours(channel, y_list):
    hours = []
    min_y = float(y_list[len(y_list) - 1])
    max_y = float(y_list[0])

    for y in y_list:
        hours_watched = (float(y) - min_y) / (max_y - min_y) * (channel.max_value - channel.min_value)
        hours.append(channel.max_value - round(hours_watched))

    return hours


def compute_daily_hours(data):
    new_data = data.copy()

    old_date = ""
    current_day = 0
    while current_day <= TOTAL_DAYS:
        date = UNIVERSAL_FIRST_DATE + timedelta(current_day)
        old_date = UNIVERSAL_FIRST_DATE + timedelta(current_day - 1)

        if current_day >= 1:
            old_date_hours = data[str(old_date)][1:]
            new_date_hours = data[str(date)][1:]
            daily_hours = [str(date)] + [x1 - x2 for (x1, x2) in zip(new_date_hours, old_date_hours)]
            new_data[str(date)] = daily_hours
        current_day += 1
    
    return new_data


def write_csv_file(data):
    with open(DATA_FILE, "w", newline="") as csv_file:
        csvwriter = csv.writer(csv_file)
        for title in data:
            csvwriter.writerow(data[title])


if __name__ == "__main__":
    data = prepare_data()
    read_text_files(channel_list, data)
    new_data = compute_daily_hours(data)
    write_csv_file(new_data)
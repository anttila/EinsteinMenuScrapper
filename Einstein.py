# -*- coding: utf-8 -*-


import urllib2
import re
import datetime


class Lunch():
    def __init__(self):
        self.date = ""
        self.weekday = ""
        self.food = []

    def show(self):
        print self.date,
        print self.weekday
        for x in self.food:
            print x

def remove_tags(s):
    # Not exactly safe, but it does the trick
    data = []
    counter = 0
    start_record = 0
    for x in xrange(len(s)):
        if s[x] == "<" or x == len(s)-1:
            if counter == 0:
                temp = s[start_record:x].strip().replace("&nbsp;", " ")
                if len(temp) != 0:
                    data.append(temp)
            counter += 1
        elif s[x] == ">":
            counter -= 1

            if counter == 0:
                start_record = x+1
    return data

def get_date(week, day):
    year = datetime.date.today().isocalendar()[0]
    # -1 on week since strptimes has an odddateformat, it counts the first week with a monday in it as the first week,
    # this is pretty bad, but works for 2015 at least
    return datetime.datetime.strptime(str(year)+"-W"+str(week-1)+"-"+str(day+1), "%Y-W%W-%w")

def create_lunch_timestamp(s):
    return s.replace("-","")+"T104500Z", s.replace("-","")+"T120000Z"

def create_ics(menu):
    file = open("test.ics",'w')
    file.write("BEGIN:VCALENDAR\n")
    file.write("VERSION:2.0\n")
    file.write("PRODID:-//Not sure/what to write//here//EN\n") # TODO
    for x in menu:
        file.write("BEGIN:VEVENT\n")
        file.write("UID:"+x.date+"\n")
        times = create_lunch_timestamp(x.date)
        file.write("DTSTART:"+times[0]+"\n")
        file.write("DTEND:"+times[1]+"\n")
        file.write("SUMMARY:Lunch\n")
        description = ""
        for i in xrange(len(x.food)):
            description += x.food[i]
            if i != len(x.food)-1:
                description += "\\n"
        file.write("DESCRIPTION:"+description.encode('latin-1')+"\n")
        file.write("END:VEVENT\n")
    file.write("END:VCALENDAR\n")
    file.close()

if __name__ == '__main__':
    # TODO: Input parameter if you just want to show the menu, or create an ICS file, or both.
    # TODO: Input parameter for filename
    # TODO: Clean up the mess bellow and move it into one or more functions instead
    # TODO: Add in support for parsing the week-long dishes

    # Replace with local copy when doing dev stuff, so nopt to spam the server
    response = urllib2.urlopen('http://www.butlercatering.se/einstein').read()
    html = response.split("\n")

    week = 0
    day_counter = -1 # -1 so that it can be incremented to 0 once the first is found
    food_counter = 0 # Find a way to remove this, only used at opne place, maybe have it look at the tag or something instead
    parsing_day = False
    menu = []
    for x in xrange(len(html)):
        if not parsing_day:
            if "lunch-titel" in html[x]:
                week = int(re.findall("\d+",html[x])[1]) # [0] will be 2 from h2, same with [2], [1] is week number
            elif "<div class=\"field-day\">" in html[x]:
                parsing_day = True
                day_counter += 1
                food_counter = 0
                menu.append(Lunch())
                menu[day_counter].date = str(get_date(week, day_counter)).split(" ")[0]
        else:
            # This assumes that the structure is always four lines: Week day, then three lines for food
            # No we are parsing a day!
            if "</div>" in html[x]:
                parsing_day = 0
            else:
                parsed_result = remove_tags(html[x].decode('utf'))[0]
                if food_counter == 0:
                    menu[day_counter].weekday = parsed_result
                else:
                    menu[day_counter].food.append(parsed_result)
                food_counter += 1

    create_ics(menu)
    #for x in menu:
    #    x.show()



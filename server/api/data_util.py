from db.mysql_engine import *

SPRING_SEM = "SP"

def convertSem(s: str):
    """
    Converts a string (e.g. "FA20") to a representative number

    :param s: string representing semester/year
    :return: integer representing semester/year
    """
    return int(s[len(SPRING_SEM):]) * 2 if s[:len(SPRING_SEM)] == SPRING_SEM else 1 + int(s[len(SPRING_SEM):]) * 2

def processSurveyData(data: dict):
    """
    Creates tuples to insert to the students and enrollments table from post request

    :param data: JSON of data from request
    :return: tuples representing students, enrollments, and tracks
    """
    startS, endS, currS, netID, name, password = data["StartingSem"], data["EndingSem"], data["CurrentSem"], data["NetID"], data["Name"], data["Password"]
    totalSem = convertSem(endS) - convertSem(startS) + 1
    student = (netID, name, password, startS, currS, endS, totalSem)

    majors, minors = list(data["Majors"]), list(data["Minors"])
    tracks = []
    for m in (majors + minors):
        tracks.append([m, "", 0, netID])

    enrollments = []
    if "classes" in data:
        for c in data["classes"]:
            enrollments.append([netID, c['Course'], c['Sem'], c['Sem'], int(c['Rating'])])

    return student, enrollments, tracks

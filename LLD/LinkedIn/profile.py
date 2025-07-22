from typing import List

class Experience:
    def __init__(self, title: str, company: str, start_date: str, end_date: str, description: str):
        self.title = title
        self.company = company
        self.start_date = start_date
        self.end_date = end_date
        self.description = description

class Education:
    def __init__(self, school: str, degree: str, field_of_study: str, start_date: str, end_date: str):
        self.school = school
        self.degree = degree
        self.field_of_study = field_of_study
        self.start_date = start_date
        self.end_date = end_date

class Skill:
    def __init__(self, name: str):
        self.name = name

class Profile:
    def __init__(self):
        self.profile_picture: str = ""
        self.headline: str = ""
        self.summary: str = ""
        self.experiences: List[Experience] = []
        self.educations: List[Education] = []
        self.skills: List[Skill] = []

    def set_summary(self, summary: str):
        self.summary = summary

    def set_headline(self, headline: str):
        self.headline = headline

    def add_experience(self, experience: Experience):
        self.experiences.append(experience)

    def add_education(self, education: Education):
        self.educations.append(education)

    def add_skill(self, skill: Skill):
        self.skills.append(skill)
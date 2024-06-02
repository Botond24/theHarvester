import random
from openai import OpenAI
from faker import Faker
import tqdm
import sqlite3
con = sqlite3.connect('stash.sqlite')

cur = con.cursor()

rows = cur.execute('SELECT DISTINCT resource FROM results WHERE type="email" ORDER BY domain').fetchall()

for row in rows:
    print(row)

OPENAI_API_KEY = "key"

openai = OpenAI(api_key=OPENAI_API_KEY)
chat = [{"role":"system","content":"You are a email helper, you create an IT support password reset email bast on a persons gender: {gender} and full name: {full_name}. You must include a return address: {email} and IT support name: {support_name}. Simple Example: Dear {full_name},\n Please click on the following link to reset your password: {reset_link}\nSincerely,\n{support_name}\n{email}"},{"role":"system","content":"Do not acknowledge the request."},{"role":"user","content":""}]

class Person:
    def __init__(self, fake: Faker):
        self.gender = random.choice(["M", "F"])
        self.first_name = fake.first_name_male() if self.gender == "M" else fake.first_name_female()
        self.last_name = fake.last_name()
        self.full_name = f"{self.first_name} {self.last_name}"
        self.email = f"{self.first_name.lower()}.{self.last_name.lower()}@{fake.free_email_domain()}"
        self.text = ""

    def __str__(self):
        return self.text

fake = Faker()
people = [Person(fake)]
link = "https://reddit.com"
pbar = tqdm.tqdm(total=51,initial=len(people))
pbar.set_description("Generating people")
for row in rows:
    person = Person(fake)
    person.email = row[0]
    chat[2]["content"] = "Generate an email for a " + "man" if person.gender == "M" else "woman" + " called " + person.full_name + " with the support name being " + people[0].full_name + " and the support email being " + people[0].email + ". The reset link should be " + link
    resp = openai.chat.completions.create(
        model="gpt-4o",
        messages= chat
    )
    ret = resp.choices[0].message.content
    ret = ret.replace("[Full Name]", person.full_name)
    ret = ret.replace("[full_name]", person.full_name)
    ret = ret.replace("{full_name}", person.full_name)
    ret = ret.replace("John Doe", person.full_name)
    ret = ret.replace("John Smith", person.full_name)
    ret = ret.replace("[Support Name]", people[0].full_name)
    ret = ret.replace("[Support_Name]", people[0].full_name)
    ret = ret.replace("[support_name]", people[0].full_name)
    ret = ret.replace("[Support Email]", people[0].email)
    ret = ret.replace("[support_email]", people[0].email)
    ret = ret.replace("{support_email}", people[0].email)
    ret = ret.replace("[email]", person.email)
    ret = ret.replace("[Email]", person.full_name)
    ret = ret.replace("{email}", person.full_name)
    ret = ret.replace("[Reset Link]", link)
    ret = ret.replace("[Reset_Link]", link)
    ret = ret.replace("[Reset Password Link]", link)
    ret = ret.replace("[reset_link]", link)
    ret = ret.replace("[reset_link]", link)
    if person.full_name not in ret or link not in ret or "Sure" in ret:
        print("skipping", person.full_name, person.full_name not in ret, link not in ret)
        print(ret)
        continue
    person.text = ret
    pbar.update(1)
    people.append(person)
print()
print(people[0].full_name, people[0].email)
print(*people, sep="\n--------------\n")
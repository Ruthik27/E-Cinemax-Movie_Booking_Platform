class Mailgun:
   __instance = None

   @staticmethod 
   def getInstance():
      if Mailgun.__instance == None:
         Mailgun()
      return Mailgun.__instance
   def __init__(self):
      if Mailgun.__instance != None:
         raise Exception("Only one Mailgun object can be created!")
      else:
         Mailgun.__instance = self


   def send_simple_message(requests):
	   return requests.post(
		"https://api.mailgun.net/v3/E-cinemaX/messages",
		auth=("api", "YOUR_API_KEY"),
		data={"from": "Excited User postmaster@sandbox92b2fca3c3f8430395f64f4d5f469413.mailgun.org",
			"to": [requests.user.email, "YOU@YOUR_DOMAIN_NAME"],
			"subject": "Email verification",
			"text": "Hi, Please click on the link to confirm your registration,"})
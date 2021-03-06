import os
import sys
import json
import signal
from pull import PULL

pull = PULL()

class PARSER:

	REGEXS = {
		"Cloudinary"  : "cloudinary://.*",
		"Firebase URL": ".*firebaseio\.com",
		"Slack Token": "(xox[p|b|o|a]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32})",
    	"RSA private key": "-----BEGIN RSA PRIVATE KEY-----",
    	"SSH (DSA) private key": "-----BEGIN DSA PRIVATE KEY-----",
    	"SSH (EC) private key": "-----BEGIN EC PRIVATE KEY-----",
    	"PGP private key block": "-----BEGIN PGP PRIVATE KEY BLOCK-----",
    	"Amazon AWS Access Key ID": "AKIA[0-9A-Z]{16}",
    	"Amazon MWS Auth Token": "amzn\\.mws\\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    	"AWS API Key": "AKIA[0-9A-Z]{16}",
    	"Facebook Access Token": "EAACEdEose0cBA[0-9A-Za-z]+",
    	"Facebook OAuth": "[f|F][a|A][c|C][e|E][b|B][o|O][o|O][k|K].*['|\"][0-9a-f]{32}['|\"]",
    	"GitHub": "[g|G][i|I][t|T][h|H][u|U][b|B].*['|\"][0-9a-zA-Z]{35,40}['|\"]",
    	"Generic API Key": "[a|A][p|P][i|I][_]?[k|K][e|E][y|Y].*['|\"][0-9a-zA-Z]{32,45}['|\"]",
    	"Generic Secret": "[s|S][e|E][c|C][r|R][e|E][t|T].*['|\"][0-9a-zA-Z]{32,45}['|\"]",
    	"Google API Key": "AIza[0-9A-Za-z\\-_]{35}",
    	"Google Cloud Platform API Key": "AIza[0-9A-Za-z\\-_]{35}",
    	"Google Cloud Platform OAuth": "[0-9]+-[0-9A-Za-z_]{32}\\.apps\\.googleusercontent\\.com",
    	"Google Drive API Key": "AIza[0-9A-Za-z\\-_]{35}",
    	"Google Drive OAuth": "[0-9]+-[0-9A-Za-z_]{32}\\.apps\\.googleusercontent\\.com",
    	"Google (GCP) Service-account": "\"type\": \"service_account\"",
    	"Google Gmail API Key": "AIza[0-9A-Za-z\\-_]{35}",
    	"Google Gmail OAuth": "[0-9]+-[0-9A-Za-z_]{32}\\.apps\\.googleusercontent\\.com",
    	"Google OAuth Access Token": "ya29\\.[0-9A-Za-z\\-_]+",
    	"Google YouTube API Key": "AIza[0-9A-Za-z\\-_]{35}",
    	"Google YouTube OAuth": "[0-9]+-[0-9A-Za-z_]{32}\\.apps\\.googleusercontent\\.com",
    	"Heroku API Key": "[h|H][e|E][r|R][o|O][k|K][u|U].*[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}",
    	"MailChimp API Key": "[0-9a-f]{32}-us[0-9]{1,2}",
    	"Mailgun API Key": "key-[0-9a-zA-Z]{32}",
    	"Password in URL": "[a-zA-Z]{3,10}://[^/\\s:@]{3,20}:[^/\\s:@]{3,20}@.{1,100}[\"'\\s]",
    	"PayPal Braintree Access Token": "access_token\\$production\\$[0-9a-z]{16}\\$[0-9a-f]{32}",
    	"Picatic API Key": "sk_live_[0-9a-z]{32}",
    	"Slack Webhook": "https://hooks.slack.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}",
    	"Stripe API Key": "sk_live_[0-9a-zA-Z]{24}",
    	"Stripe Restricted API Key": "rk_live_[0-9a-zA-Z]{24}",
    	"Square Access Token": "sq0atp-[0-9A-Za-z\\-_]{22}",
    	"Square OAuth Secret": "sq0csp-[0-9A-Za-z\\-_]{43}",
    	"Twilio API Key": "SK[0-9a-fA-F]{32}",
    	"Twitter Access Token": "[t|T][w|W][i|I][t|T][t|T][e|E][r|R].*[1-9][0-9]+-[0-9a-zA-Z]{40}",
    	"Twitter OAuth": "[t|T][w|W][i|I][t|T][t|T][e|E][r|R].*['|\"][0-9a-zA-Z]{35,44}['|\"]"
	}

	def __init__(self, opts):
		if opts.help:
			pull.help()

		self.depth     = opts.depth if opts.depth >= 0 else pull.halt("Invalid Depth Provided!", exit=1)
		self.list      = self.target(opts.target)
		self.regexs    = self.regexs(opts.regex, opts.regfile)
		self.verbose   = opts.verbose
		#self.signal    = signal.signal(signal.SIGINT, self.handler)

	def handler(self, sig, fr):
		pull.halt("Received Interrupt!", exit=0)

	def enum_files(self, tgt, depth=1):
		rtval = []

		llist = os.listdir(tgt)
		for ll in llist:
			path = os.path.join(tgt, ll)

			if os.path.isfile(path):
				rtval.append(path)
			elif os.path.isdir(path):
				if self.depth == -0 or depth < self.depth:
					sublist = self.enum_files(path, depth+1)
					for elem in sublist:
						rtval.append(elem)

		return rtval

	def target(self, tgt):
		rtval = []

		if tgt:
			if os.path.isfile(tgt):
				rtval.append( tgt )
			elif os.path.isdir(tgt):
				rtval = self.enum_files(tgt)
			else:
				pull.halt("Target Directory/File Does not Exist!", 1)
		else:
			pull.halt("Target Directory/File Not Provided!", 1)

		return rtval

	def regexs(self, regex, regexfl):
		if regex or regexfl:
			if regex and regexfl:
				pull.halt("Both --regex and --regex-json can't be Provided At Same!", exit=1)
			else:
				if regex:
					return {'Given Regex': regex}
				else:
					if os.path.isfile(regexfl):
						fl = open(regexfl)
						try:
							rtval = json.loads(fl.read())
						except:
							pull.halt("Not a Valid JSON File!", exit=1)
						return rtval
					else:
						pull.halt("Regex File Not Found! ", exit=1)
		else:
			pull.info("No Regex Provided. Will Use Inner Regexs")
			return self.REGEXS
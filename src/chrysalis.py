import os
import subprocess
import pathlib
import sys
import argparse
import json
from dotenv import load_dotenv

from Utilities.Arguments import args
from Utilities.Logger import Logger
from Subscription import Subscription

load_dotenv()

config_dir = 'configs'


with open('src/subscriptions.json', 'r') as myfile:
    subscription_encoded=myfile.read()

subscriptions = json.loads(subscription_encoded)

def process_subscription(subscription: Subscription):
	output_dir = os.getenv('staging_directory') + '/' + subscription.name

	archive_path = os.path.join(output_dir, 'downloaded.log')
	config_path = os.path.join(config_dir, subscription.youtubedl_config.config)

	output_format = output_dir + '/staging_area/' + subscription.youtubedl_config.output_format

	pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True) 

	command =  r'youtube-dl'
	command += r' --config-location "{}"'.format(config_path)
	command += r' --metadata-from-title "{}"'.format(subscription.youtubedl_config.metadata_format)
	command += r' -o "{}"'.format(output_format)
	command += r' --download-archive "{}"'.format(archive_path)
	command += r' "{}"'.format(subscription.url)
	command += ' --exec \'"{}" "{}" --rename {{}} --subscription "{}"\''.format(
		sys.executable, 
		__file__, 
		subscription.name
	)

	if subscription.logging.path:
		command += r' {} "{}"'.format(
			'>>' if subscription.logging.append == True else '>',
			subscription.logging.path
		)

	subprocess.run(command, shell=True)


def rename(file: str, subscription: Subscription) -> (str, int):
	from Renamer import Renamer

	Logger.log(r'Crysalis', r'Starting Renamer for {}'.format(file), 1)

	renamer = Renamer(
		file = file,
		settings = subscription
	)

	(new_folder, season) = renamer.rename()

	Logger.tab -= 1

	return (new_folder, season)


def move_from_staging_area(current_path: str, subscription: Subscription, season: int):
	current_path = pathlib.Path(current_path)

	out_dir = subscription.post_processing.output_directory

	pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True) 

	final_dir = out_dir + '/' + current_path.name

	current_path.rename(final_dir)

	Logger.log(r'[Renamer]', r'Refoldered to {}'.format(final_dir))
	
	





if args.rename is not None:
	subs = [item for item in subscriptions if item['name'] == args.subscription]

	subscription = subs[0] if subs else None

	if not subscription:
		exit(-1)

	(new_folder, season) = rename(args.rename, subscription)
	move_from_staging_area(new_folder, subscription, season)
else:
	for subscription in subscriptions:
		process_subscription(Subscription(dict_config = subscription))
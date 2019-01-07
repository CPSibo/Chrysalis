import os
import subprocess
import pathlib
import sys
import argparse
from dotenv import load_dotenv

from Subscriptions import SUBSCRIPTIONS
from Arguments import args
from Logger import Logger

load_dotenv()

config_dir = 'configs'


def process_subscription(subscription):
	output_dir = os.getenv('staging_directory') + '/' + subscription['name']

	archive_path = os.path.join(output_dir, 'downloaded.log')
	log_path = os.path.join(output_dir, 'youtube-dl.log')
	config_path = os.path.join(config_dir, subscription['config'])

	output_format = output_dir + '/staging_area/' + subscription['output format']

	pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True) 

	command = r'youtube-dl' +\
		r' --config-location "' + config_path + r'"' +\
		r' --metadata-from-title "' + subscription['metadata format'] + r'"' +\
		r' -o "' + output_format + r'"' +\
		r' --download-archive "' + archive_path + r'"' +\
		r' "' + subscription['url'] + r'"' +\
		' --exec \'"{}" "{}" --rename {{}} --subscription "{}"\''.format(
			sys.executable, 
			__file__, 
			subscription['name']
		) +\
		r' > "' + log_path + r'"'

	subprocess.run(command, shell=True)


def rename(file, subscription):
	from Renamer import Renamer

	Logger.log(r'Crysalis', r'Starting Renamer for {}'.format(file), 1)

	renamer = Renamer(
		file = file,
		settings = subscription
	)

	(new_folder, season) = renamer.rename()

	Logger.tab -= 1

	return (new_folder, season)


def move_from_staging_area(current_path, subscription, season):
	current_path = pathlib.Path(current_path)

	out_dir = subscription['rename output']['output directory']

	if subscription['rename output']['folder by season']:
		season = 'Season {:02d}'.format(season)

		if season == 'Season 00':
			season = 'Specials'

		out_dir = out_dir + '/' + season

	pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True) 

	final_dir = out_dir + '/' + current_path.name

	current_path.rename(final_dir)

	Logger.log(r'[Renamer]', r'Refoldered to {}'.format(final_dir))
	





if args.rename is not None:
	subs = [item for item in SUBSCRIPTIONS if item['name'] == args.subscription]

	subscription = subs[0] if subs else None

	if not subscription:
		exit(-1)

	(new_folder, season) = rename(args.rename, subscription)
	move_from_staging_area(new_folder, subscription, season)
else:
	for subscription in SUBSCRIPTIONS:
		process_subscription(subscription)
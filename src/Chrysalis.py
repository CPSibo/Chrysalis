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

# Description:
# 	The entry point for Chrysalis.
#
# Params:
#	none
class Chrysalis:

	# region Attributes

	# Decoded subscription settings.
	subscriptions = []

	# endregion



	# region Constructors

	def __init__(self):
		load_dotenv()

		self.load_subscriptions()

	# endregion



	# region Functions

	# Description:
	# 	Reads in subscriptions.json and decodes all the
	# 	settings into Subscription objects.
	#
	# Params:
	#	none
	#
	# Returns: 
	# 	void
	def load_subscriptions(self):
		with open('src/subscriptions.json', 'r') as myfile:
			subscription_encoded=myfile.read()

		subscriptions_decoded = json.loads(subscription_encoded)

		self.subscriptions = []

		for sub in subscriptions_decoded:
			self.subscriptions.append(Subscription(dict_config = sub))



	# Description:
	# 	Runs youtube-dl and the post-processing for the given
	# 	subscription.
	#
	# Params:
	#	Subscription subscription: The subscription to process.
	#
	# Returns: 
	# 	void
	def process_subscription(self, subscription: Subscription):
		self.setup_staging_directory(subscription)

		command = self.construct_command(subscription)

		subprocess.run(command, shell=True)



	# Description:
	#	Constructs and creates the staging directory
	# 	for the given subscription.
	#
	# Params:
	#	Subscription subscription: The subscription to process.
	#
	# Returns:
	#	str: The path to the staging directory.
	def setup_staging_directory(self, subscription: Subscription) -> str:
		pathlib.Path(subscription.staging_directory).mkdir(parents=True, exist_ok=True) 

		return subscription.staging_directory



	# Description:
	#	Builds the youtube-dl command for the given subscription.
	#
	# Params:
	#	Subscription subscription: The subscription to process.
	#
	# Returns:
	#	str: The youtube-dl command with all desired arguments.
	def construct_command(self, subscription: Subscription) -> str:
		command =  r'youtube-dl'

		# Add the youtube-dl config path.
		if subscription.youtubedl_config.config:
			config_path = os.path.join(os.getenv('youtubedl_config_directory'), subscription.youtubedl_config.config)
			command += r' --config-location "{}"'.format(config_path)

		# Add the metadata-from-title pattern.
		if subscription.youtubedl_config.metadata_format:
			command += r' --metadata-from-title "{}"'.format(subscription.youtubedl_config.metadata_format)

		# Add the output pattern.
		if subscription.youtubedl_config.output_format:
			output_format = subscription.staging_directory + '/staging_area/' + subscription.youtubedl_config.output_format
			command += r' -o "{}"'.format(output_format)

		# Add the path to the video ID archive.
		if subscription.youtubedl_config.archive:
			archive_path = os.path.join(subscription.staging_directory, subscription.youtubedl_config.archive)
			command += r' --download-archive "{}"'.format(archive_path)

		# Add any extra arguments this sub has.
		if subscription.youtubedl_config.extra_commands:
			command += " " + subscription.youtubedl_config.extra_commands

		# Add the subscription URL.
		command += r' "{}"'.format(subscription.url)

		# Construct the post-processing call back into 
		# Chrysalis to be run after each successful download.
		if subscription.post_processing:
			command += ' --exec \'"{}" "{}" --rename {{}} --subscription "{}"\''.format(
				sys.executable, 
				__file__, 
				subscription.name
			)

		# Construct the stdout redirect to the log file.
		if subscription.logging.path:
			command += r' {} "{}"'.format(
				'>>' if subscription.logging.append == True else '>',
				subscription.logging.path
			)

		return command



	# Description:
	# 	Runs the post-processing for the given youtube-dl output file.
	#
	# Params:
	#	str file:                  Absolute path to the youtube-dl output file.
	#	Subscription subscription: The settings to process the file under.
	#
	# Returns:
	#	str: The absolute path to the folder where all the files were moved.
	#	int: The season number of the file processed.
	def rename(self, file: str, subscription: Subscription) -> (str, int):
		from Renamer import Renamer

		Logger.log(r'Crysalis', r'Starting Renamer for {}'.format(file), 1)

		renamer = Renamer(
			file = file,
			settings = subscription
		)

		(new_folder, season) = renamer.rename()

		Logger.tab -= 1

		return (new_folder, season)



	# Description:
	# 	Moves the post-processed folder from the staging area
	# 	to the final path specified by the subscription.
	#
	# Params:
	#	str current_path:          The absolute path to the staging-area folder.
	#	Subscription subscription: The settings under which to process
	#							   the files.
	#	int season:                The season number for episode processed.
	#
	# Returns:
	#	void
	def move_from_staging_area(self, current_path: str, subscription: Subscription, season: int):
		current_path = pathlib.Path(current_path)

		out_dir = subscription.post_processing.output_directory

		pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True) 

		final_dir = out_dir + '/' + current_path.name

		current_path.rename(final_dir)

		Logger.log(r'[Renamer]', r'Refoldered to {}'.format(final_dir))



	# Description:
	# 	Entry point for the Chrysalis process.
	#
	# Params:
	#	none
	#
	# Returns:
	#	int: Status code.
	def run(self) -> int:
		if args.rename is not None:
			subs = [item for item in self.subscriptions if item['name'] == args.subscription]

			subscription = subs[0] if subs else None

			if not subscription:
				return -1

			(new_folder, season) = self.rename(args.rename, subscription)
			self.move_from_staging_area(new_folder, subscription, season)
		else:
			for subscription in self.subscriptions:
				self.process_subscription(subscription)

	# endregion

Chrysalis().run()
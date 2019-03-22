# region Imports

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
from Repositories import REPOSITORIES
from Destinations import DESTINATIONS

# endregion



class Chrysalis:
	"""
	The entry point for Chrysalis.

	Attributes:
		subscriptions (dict): Decoded subscription settings.
	"""

	# region Attributes

	subscriptions = []

	# endregion



	# region Constructors

	def __init__(self):
		load_dotenv()

		self.load_subscriptions()

	# endregion



	# region Functions

	def load_subscriptions(self):
		"""
		Reads in subscriptions.json and decodes all the settings 
		into Subscription objects.
		"""

		with open('src/subscriptions.json', 'r') as myfile:
			subscription_encoded=myfile.read()

		subscriptions_decoded = json.loads(subscription_encoded)

		self.subscriptions = []

		for sub in subscriptions_decoded:
			self.subscriptions.append(Subscription(dict_config = sub))



	def process_subscription(self, subscription: Subscription):
		"""
		Runs youtube-dl and the post-processing for the given subscription.

		Parameters:
			subscription (Subscription): The subscription to process.
		"""

		if not subscription.enabled:
			return

		Logger.log(r'Chrysalis', r'Processing "{}"...'.format(subscription.name))

		self.setup_staging_directory(subscription)

		if subscription.logging and subscription.logging.path:
			pathlib.Path(subscription.logging.path).parent.mkdir(parents=True, exist_ok=True) 

		command = self.construct_command(subscription)

		subprocess.run(command, shell=True)



	def setup_staging_directory(self, subscription: Subscription) -> str:
		"""
		Constructs and creates the staging directory for the given subscription.

		Parameters:
			subscription (Subscription): The subscription to process.

		Returns:
			str: The path to the staging directory.
		"""

		pathlib.Path(subscription.staging_directory).mkdir(parents=True, exist_ok=True) 

		return subscription.staging_directory



	def construct_command(self, subscription: Subscription) -> str:
		"""
		Builds the youtube-dl command for the given subscription.
		
		Args:
			subscription (Subscription): The subscription to process.
		
		Returns:
			str: The youtube-dl command with all desired arguments.
		"""

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
			command += ' --exec \'"{}" "{}" --postprocess {{}} --subscription "{}"\''.format(
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

		Logger.log(r'Chrysalis', r'Command to be run: [{}]'.format(command))

		return command



	def postprocess(self, file: str, subscription: Subscription) -> str:
		"""
		Runs the post-processing for the given youtube-dl output file.
		
		Args:
			file (str): Absolute path to the youtube-dl output file.
			subscription (Subscription): The settings to process the file under.
		
		Returns:
			str: The absolute path to the folder where all the files were moved.
		"""

		from PostProcessor import PostProcessor

		Logger.log(r'Crysalis', r'Starting PostProcessor for {}'.format(file), 1)

		postprocessor = PostProcessor(
			file = file,
			settings = subscription
		)

		postprocessor.run()

		Logger.tabs -= 1



	def run(self) -> int:
		"""
		Entry point for the Chrysalis process.
		
		Returns:
			int: Status code.
		"""

		if args.postprocess is not None:
			subs = [item for item in self.subscriptions if item.name == args.subscription]

			subscription = subs[0] if subs else None

			if not subscription:
				return -1

			self.postprocess(args.postprocess, subscription)
		else:
			for subscription in self.subscriptions:
				self.process_subscription(subscription)

	# endregion



Chrysalis().run()
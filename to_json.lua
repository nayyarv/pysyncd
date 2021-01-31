#!/usr/local/bin/env lua

local luna = require 'lunajson'
local data = loadfile("/Users/varun/.lsyncd")
print(data())

local settings = {
    logfile    = "/tmp/lsyncd.log",
    statusFile = "/tmp/lsyncd.status",
    nodaemon   = true,
}

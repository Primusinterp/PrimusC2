#Copyright (c) 2022 Itay Migdal

import std/[macros, times, md5]
import strutils
import sequtils
import RC4

macro obfi*(data: static[string]): string =
  let key = getMD5($cpuTime())
  let encrypted_data = toRC4(key, data)
  let encrypted_data_nn = newLit(encrypted_data)
  let key_nn = newLit(key)
  quote do:
    fromRC4(`key_nn`, `encrypted_data_nn`)

macro splitString*(data: static[string]): string =
  let splited = toSeq(data.items)
  let splited_nn = newLit(splited)
  quote do:
    join(`splited_nn`)
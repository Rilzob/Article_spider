# encoding:utf-8

# @Author: Rilzob
# @Time: 2018/10/24 下午1:51

import redis
redis_cli = redis.StrictRedis()
redis_cli.incr("jobbole_count")

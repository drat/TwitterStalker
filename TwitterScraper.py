import time
import sys

import tweepy
from tweepy import Cursor
#get tweepy set up
consumer_key="5Axgirp7hRTs4sxskrX4rg"
consumer_secret="cLZ2U7tEQA3ROqd0f8SclUYgodwRmhHQ97YXs7KDCg8"
access_token="28881634-yLi7SYhLaAI6q9giw8jFvlFWahmhXtYoBYPCbjX9T"
access_token_secret="QW6MlErVIFG2Iq3VxeYgCeG6Mw2Zx4PbECehMSF8ANnxw"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

#get neo4j set up
#note, you have to have neo4j running and on the default port
from py2neo import neo4j
graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data")



neo4j.CypherQuery(graph_db,"""
    CREATE CONSTRAINT ON (u:User) 
    ASSERT u.str_id IS UNIQUE
""").execute()


def create_or_get_node(twitter_user,labels=[]):
    data = {'id_str': twitter_user.id_str,
        'name': twitter_user.name,
        'screen_name': twitter_user.screen_name,
        'description': twitter_user.description,
        'url': twitter_user.url,
        'followers_count': twitter_user.followers_count,
        'friends_count': twitter_user.friends_count,
        'listed_count': twitter_user.listed_count,
        'statuses_count': twitter_user.statuses_count,
        'favourites_count': twitter_user.favourites_count,
        'location': twitter_user.location,
        'time_zone': twitter_user.time_zone,
        'utc_offset': twitter_user.utc_offset,
        'lang': twitter_user.lang,
        'profile_image_url': twitter_user.profile_image_url,
        'geo_enabled': twitter_user.geo_enabled,
        'verified': twitter_user.verified,
        'notifications': twitter_user.notifications,
    }
    query_string = """
        MERGE (u:User {id_str:{id_str}}) 
        ON CREATE SET
"""+   (('u:'+',u:'.join(labels)+",") if labels else '') +"""
            u.name={name},
            u.screen_name={screen_name},
            u.description={description},
            u.url={url},
            u.followers_count={followers_count},
            u.friends_count={friends_count},
            u.listed_count={listed_count},
            u.statuses_count={statuses_count},
            u.favourites_count={favourites_count},
            u.location={location},
            u.time_zone={time_zone},
            u.utc_offset={utc_offset},
            u.lang={lang},
            u.profile_image_url={profile_image_url},
            u.geo_enabled={geo_enabled},
            u.verified={verified},
            u.notifications={notifications}
""" +   (("ON MATCH SET\n  u:"+',u:'.join(labels)) if labels else '') +"""
        RETURN u
    """
    n=neo4j.CypherQuery(graph_db,query_string).execute_one(**data)
    return n


def insert_user_with_friends(twitter_user,user_labels=[]):
    user_labels.append("SeedNode")
    if isinstance(twitter_user, basestring):
        try:
            twitter_user = api.get_user(twitter_user)
        except:
            time.sleep(60 * 16)
            friend = friends.next()
    create_or_get_node(twitter_user,user_labels)
    friend_count = 0
    print u"\nINSERTING FOR: {}".format(twitter_user.name)
    friends = Cursor(api.friends, user_id=twitter_user.id_str, count=200).items()
    try:
        while True:
            try:
                friend = friends.next()
            except tweepy.TweepError:
                print "exceeded rate limit. waiting"
                time.sleep(60 * 16)
                friend = friends.next()
            
            #print u"    INSERTING: {}".format(friend.name)
            friend_count += 1
            sys.stdout.write('.')
            if(friend_count%10 == 0): sys.stdout.write(' ')
            if(friend_count%50 == 0): sys.stdout.write('| ')
            if(friend_count%100 == 0): print

            
            create_or_get_node(friend)
            n=neo4j.CypherQuery(graph_db,"""
                MATCH (user:User {id_str:{user_id_str}}),(friend:User {id_str:{friend_id_str}})
                CREATE UNIQUE (user)-[:FOLLOWS]->(friend)
            """).execute_one(user_id_str=twitter_user.id_str, friend_id_str=friend.id_str)            
    except StopIteration:
        print u"\n    Total Friend Count = {}".format(friend_count)




#Add me and all my colleagues to the db along with all of our friends.
insert_user_with_friends('softwaredoug',["OSC"])
insert_user_with_friends('jnbrymn',["OSC","Neo"])
insert_user_with_friends('patriciagorla',["OSC"])
insert_user_with_friends('scottstults',["OSC"])
insert_user_with_friends('dep4b',["OSC","Neo"])
insert_user_with_friends('o19s',["OSC"])
insert_user_with_friends('jwoodell',["OSC"])
insert_user_with_friends('omnifroodle',["OSC"])
insert_user_with_friends('danielbeach',["OSC"])
 
 
##Add prominent Neo folks and those they follow
insert_user_with_friends('neo4j',["Neo"])
insert_user_with_friends('mesirii',["Neo"])
insert_user_with_friends('emileifrem',["Neo"])
insert_user_with_friends('jimwebber',["Neo"])
insert_user_with_friends('peterneubauer',["Neo"])
insert_user_with_friends('p3rnilla',["Neo"])
insert_user_with_friends('maxdemarzi',["Neo"])
insert_user_with_friends('rvanbruggen',["Neo"])
insert_user_with_friends('wefreema',["Neo"])
insert_user_with_friends('ayeeson',["Neo"])
insert_user_with_friends('akollegger',["Neo"])
insert_user_with_friends('markhneedham',["Neo"])
insert_user_with_friends('technige',["Neo"])
 
#Now you add yourself and add those that you find interesting.

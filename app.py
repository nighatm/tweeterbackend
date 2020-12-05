import mariadb
from flask import Flask, request, Response
import json
import dbcreds
from flask_cors import CORS
import random
import string

app = Flask(__name__)
CORS(app)
# GENERATE LOGIN TOKEN
def get_loginToken(length):
    password_characters = string.ascii_letters + string.digits
    login_token = ''.join(random.choice(password_characters) for i in range(length))
    return login_token

# USER LOGGING IN LOGGING OUT 
@app.route('/api/login', methods=['POST', 'DELETE'])
def login():
    if request.method == 'POST':
        conn = None
        cursor = None
        userEmail = request.json.get("email")
        userPassword = request.json.get("password")
        rows = None
        user = None
        user_info = {}
        
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email=? and password=?", [userEmail, userPassword])
            user = cursor.fetchall()
            rows = cursor.rowcount
            if (rows == 1):
                loginToken = get_loginToken(30)
                print(loginToken)
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES(?,?)", [user[0][0], loginToken])
                conn.commit()
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                user_info = {
                    "email": user[0][1],
                    "username": user[0][2],
                    "bio": user[0][4],
                    "birthdate": user[0][5],
                    "userId": user[0][0],
                    "loginToken": loginToken
                }
                return Response(json.dumps(user_info, default=str), mimetype="application/json", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        loginToken = request.json.get("loginToken")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_session WHERE loginToken = ?", [loginToken,])
            conn.commit()
            rows = cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)        
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("Successfully Logged out!", mimetype = "text/html", status = 201)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)

# CREATE USERS, GET THEIR INFORMATION, UPDATE, DELETE A USER
@app.route('/api/users', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def users():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        users_dict={}
        users_info=[]
        user_Id = request.args.get("id")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            if user_Id == None and user_Id == "":
                cursor.execute("SELECT * FROM user WHERE id=?", [user_Id,])
            else:
                cursor.execute("SELECT * FROM user")
            rows = cursor.fetchall()
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows):
                users=[]
                for row in rows:
                    users_dict={
                        "userId": row[0],
                        "email" : row[1],
                        "username": row[2],
                        "bio": row[4],
                        "birthdate" : row[5]
                    }
                    users_info.append(users_dict)
                return Response(json.dumps(users_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        user_info={}
        userEmail = request.json.get("email")
        userName = request.json.get("username")
        userPassword = request.json.get("password")
        userBio = request.json.get("bio")
        userBirthdate = request.json.get("birthdate")
       
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("INSERT INTO user(email, username, password, bio, birthdate) VALUES (?,?,?,?,?)", [userEmail, userName, userPassword, userBio, userBirthdate, ])
            user_id = cursor.lastrowid
            rows = cursor.rowcount
            if rows == 1:
                loginToken = get_loginToken(30)
                print(loginToken)
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES(?,?)", [user_id, loginToken])
                conn.commit()
                rows = cursor.rowcount
                print(rows)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                user_info = {
                    "email": userEmail,
                    "username": userName,
                    "bio": userBio,
                    "birthdate": userBirthdate,
                    "userId": user_id,
                    "loginToken": loginToken
                }
                return Response(json.dumps(user_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        user = None
        users_data={}
        userBio = request.json.get("bio")
        loginToken = request.json.get("loginToken")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken = ?",[loginToken,])
            user_update = cursor.fetchone()
            print(user_update)
            if user_update:
                if (userEmail != "" and userEmail != None):
                    cursor.execute("UPDATE user SET email = ? WHERE id = ?", [userEmail, user_update[0],])
                if (userName != "" and userName != None):
                    cursor.execute("UPDATE user SET username = ? WHERE id = ?", [userName, user_update[0],])
                if (userPassword != "" and userPassword != None):
                    cursor.execute("UPDATE user SET password = ? WHERE id = ?", [userPassword, user_update[0],])
                if (userBio != "" and userBio != None):
                    cursor.execute("UPDATE user SET bio = ? WHERE id = ?", [userBio, user_update[0],])
                if (userBirthdate != "" and userBirthdate != None):
                    cursor.execute("UPDATE user SET birthdate = ? WHERE id = ?", [userBirthdate, user_update[0]],)
                conn.commit()
                rows = cursor.rowcount
                cursor.execute("SELECT * FROM user WHERE id=?", [user_update[0],])
                user = cursor.fetchall()
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows != None): 
                users_data={
                        "userId": user_update[0],
                        "email" : user[0][1],
                        "username": user[0][2],
                        "bio": user[0][3],
                        "birthdate" : user[0][4],
                    } 
                return Response(json.dumps(users_data, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)           
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        userPassword = request.json.get("password")
        loginToken = request.json.get("loginToken")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken=?", [loginToken,])
            user = cursor.fetchone()
            print(user)
            if user !=None:
                cursor.execute("DELETE FROM user WHERE id=? AND password=?", [user[0],userPassword, ])            
            rows= cursor.rowcount      
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows != None):
                return Response("Account deleted!", mimetype = "text/html", status = 204)
            else:
                return Response("Error occured while deleting your account...", mimetype = "text/html", status = 500)

# CREATE A TWEET, GET TWEETS, UPDATE AND DELETE A TWEET  
@app.route('/api/tweets', methods=[ 'GET','POST', 'DELETE','PATCH'])
# GET WILL SEND BACK TWEET FROM A SPECIFIC USER OR ALL USERS
def tweets():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        tweets_info=[]
        tweet_dict={}
        user_id = request.args.get("userId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            if user_id == None:
                cursor.execute("SELECT t.id, t.userId, t.content, t.createdAt, u.username FROM tweet t INNER JOIN user u ON t.userId = u.id")
            else:
                cursor.execute("SELECT t.id, t.userId, t.content, t.createdAt, u.username FROM tweet t INNER JOIN user u ON t.userId = u.id WHERE u.id=?", [user_id, ])
            rows = cursor.fetchall()
            print (rows)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows!= None):
                for row in rows:
                    tweet_dict={
                        "tweetId": row[0],
                        "userId" : row[1],
                        "content": row[2],
                        "createdAt" : row[3],
                        "username": row[4]
                    }
                    tweets_info.append(tweet_dict)
                return Response(json.dumps(tweets_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    # CREATE A NEW TWEET
    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        tweetId=None
        createdAt=None
        tweet_info={}
        loginToken = request.json.get("loginToken")
        tweet_content = request.json.get("content")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()           
            cursor.execute("SELECT * FROM user_session WHERE loginToken =?", [loginToken,])
            user=cursor.fetchall()
            print(user)
            if user !=None:
                cursor.execute("INSERT INTO tweet(userId, content) VALUES(?,?)", [user[0][0],tweet_content, ])
                conn.commit()
                rows= cursor.rowcount      
                print (tweetId)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows==1):
                tweet_info={
                    "tweetId": tweetId,
                    "userId" : user[0][0] ,
                    "content": tweet_content,
                    "createdAt" :createdAt ,
                    "username": user[0][1],
                    }
                return Response(json.dumps(tweet_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
# UPDATE A TWEET
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        updated_tweet = None
        user=None
        updatedtweet_info={}
        loginToken = request.json.get("loginToken")
        tweetId = request.json.get("tweetId")
        tweet_content = request.json.get("content")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()

            cursor.execute("SELECT * FROM user_session WHERE loginToken =? ", [loginToken,])
            user=cursor.fetchall()

            cursor.execute("UPDATE tweet SET content = ? WHERE id=? AND userId=?", [tweet_content,tweetId,user[0][0] ])
            conn.commit()
            rows = cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                updatedtweet_info={
                    "tweetId": tweetId,
                    "content": tweet_content,
                    }
              
                return Response(json.dumps(updatedtweet_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    # DELETE A TWEET 
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        user = None
        loginToken = request.json.get("loginToken")
        tweetId = request.json.get("tweetId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken=?", [loginToken,])
            user = cursor.fetchone()
            print(user)
            if user !=None:
                cursor.execute("DELETE FROM tweet WHERE id=? AND userId=?", [tweetId,user[0],])
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):           
                return Response("Deleted successfully", default=str, mimetype="application/json", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

# USERS HAVE ABILITY TO COMMENT ON TWEETS, EDIT, AND DELETE COMMENTS
@app.route('/api/comments', methods=[ 'GET', 'POST', 'PATCH', 'DELETE'])
# SEND BACK COMMENTS ON TWEETS
def comments():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        comments_info=[]
        comment_dict={}
        tweet_Id = request.args.get("tweetId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            if tweet_Id == None and tweet_Id == "":
                cursor.execute("SELECT * FROM comment c INNER JOIN tweet t ON c.tweetId = t.id")
            else:
                cursor.execute("SELECT * FROM comment c INNER JOIN tweet t ON c.tweetId = t.id WHERE tweetId=?", [tweet_Id],)
            rows = cursor.fetchall()
            print (rows)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows!= None):
                tweets=[]
                for row in rows:
                    comments_dict={
                        "commentId": row[0],
                        "tweetId" : row[1],
                        "userId": row[2],
                        "content": row[3],
                        "createdAt" : row[4],
                        "username": row[5]
                    }
                    comments_info.append(comments_dict)
                return Response(json.dumps(comments_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    # CREATE NEW COMMENT ON A SPECIFIC TWEET
    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        createdAt=None
        comments_info={}
        loginToken = request.json.get("loginToken")
        content = request.json.get("content")
        tweet_Id = request.json.get("tweetId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()           
            cursor.execute("SELECT userId FROM user_session WHERE loginToken =?", [loginToken,])
            user=cursor.fetchall()
            print(user)
            if user !=None:
                cursor.execute("INSERT INTO comment(tweetId, userId, content) VALUES(?,?,?)", [tweet_Id,user[0][0],content, ])
                conn.commit()
                rows= cursor.rowcount
                cursor.execute("SELECT c.*, u.username FROM comment c INNER JOIN user u ON u.id = c.userId WHERE c.tweetId = ?",[tweet_Id, ] )
                user=cursor.fetchall()
      
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows==1):
                comments_info={
                    "commentId": user[0][0],
                    "tweetId": tweet_Id,
                    "userId" : user[0][2] ,
                    "username":user[0][5] ,
                    "content": content,
                    "createdAt" :createdAt ,
                    }
                return Response(json.dumps(comments_info, default=str), mimetype="application/json", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    # UPDATE A COMMENT
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        updated_comment = None
        user=None
        createdAt=None
        updatedcomment_info={}
        loginToken = request.json.get("loginToken")
        comment_Id = request.json.get("commentId")
        comment_content = request.json.get("content")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()

            cursor.execute("SELECT * FROM user_session WHERE loginToken =? ", [loginToken,])
            user=cursor.fetchall()
            
            cursor.execute("SELECT userId FROM comment WHERE id =? ", [comment_Id,])
            user=cursor.fetchall()

            cursor.execute("UPDATE comment SET content = ? WHERE id=? AND userId=?", [comment_content,comment_Id,user[0][0], ])
            conn.commit()
            rows = cursor.rowcount
            
            cursor.execute("SELECT c.*, u.username FROM user u INNER JOIN comment c ON u.id = c.userId WHERE c.id=?", [comment_Id,])
            user=cursor.fetchall()
            print(user)

        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                updatedcomment_info={
                    "commentId": comment_Id,
                    "tweetId":user[0][1],
                    "userId": user[0][2],
                    "username":user[0][5] ,
                    "content": comment_content,
                    "createdAt": createdAt
                    }
              
                return Response(json.dumps(updatedcomment_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
                
# DELETE A COMMENT
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        user = None
        loginToken = request.json.get("loginToken")
        comment_Id = request.json.get("commentId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken=?", [loginToken,])
            user = cursor.fetchone()
            print(user)
            if user !=None:
                cursor.execute("DELETE FROM comment WHERE id=? AND userId=?", [comment_Id,user[0],])
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):           
                return Response("Comment deleted successfully", default=str, mimetype="application/json", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

# FOLLOW IS WHEN A USER "FOLLOWS" ANOTHER USER
@app.route('/api/follows', methods=[ 'GET','POST', 'POST','DELETE'])
# SEND BACK INFORMATION ABOUT ALL THE USERS BEING FOLLOWED BY A USER "BASED ON USERID"
def follows():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        follows_info=[]
        follows_dict={}
        userId = request.args.get("userId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT u.id, u.email, u.username, u.bio, u.birthdate FROM user u INNER JOIN follow f ON u.id = f.followId WHERE f.followerId=? ", [userId, ])
            rows = cursor.fetchall()
            print(rows)

        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows != None):
                for row in rows:
                    follows_dict={
                        "userId":row[0],
                        "email":row[1],
                        "username": row[2],
                        "bio": row[3],
                        "birthdate": row[4],
                    } 
                    follows_info.append(follows_dict)        
                return Response(json.dumps(follows_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

    # CREATE A "FOLLOW" RELATIONSHIP BETWEEN 2 USERS
    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        follower = None
        loginToken = request.json.get("loginToken")
        followId = request.json.get("followId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            print(loginToken)
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [loginToken, ])
            follower = cursor.fetchall()
            print(follower)
            if follower != None:
                cursor.execute("INSERT INTO follow(followId, followerId) VALUES (?, ?)", [followId,follower[0][0], ] )
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("Successfully Followed", mimetype="application/json", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

    # DELETE A FOLLOW RELATIONSHIP "UNFOLLOW A USER"
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        user = None
        loginToken = request.args.get("loginToken")
        followId = request.args.get("followId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken=?", [loginToken,])
            user = cursor.fetchone()
            print(user)
            if user !=None:
                cursor.execute("DELETE FROM follow WHERE followId=? AND userId=?", [followId,user[0],])
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):           
                return Response(json.dumps("Comment deleted successfully", default=str), mimetype="application/json", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

# WILL SEND BACK INFORMATION ABOUT ALL USERS BEING FOLLOWED BY A USER "FOLLOWER"
@app.route('/api/followers', methods=[ 'GET'])
def followers():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        follower_info=[]
        follower_dict={}
        userId = request.args.get("userId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT u.id, u.email, u.bio, u.username, u.birthdate FROM user u INNER JOIN follow f ON u.id = f.followerId WHERE f.followId=? ", [userId, ])
            rows = cursor.fetchall()
            print(rows)

        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows != None):
                for row in rows:
                    follower_dict={
                        "userId":row[0],
                        "email":row[1],
                        "username": row[2],
                        "bio": row[3],
                        "birthdate": row[4],
                    } 
                follower_info.append(follower_dict)        
                return Response(json.dumps(follower_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

# USERS HAVE ABILITY TO LIKE TWEETS AND UNLIKE TWEETS THEY HAVE ALREADY LIKED
@app.route('/api/tweet-likes', methods=[ 'GET', 'POST', 'DELETE'])
def tweetLikes():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        tweetlike_info=[]
        tweetlike_dict={}
        tweetId = request.args.get("tweetId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            if tweetId != None and tweetId != "":
                cursor.execute("SELECT tl.tweetId, tl.userId, u.username FROM tweet_like tl INNER JOIN user u ON u.id = tl.userId WHERE tl.tweetId = ?", [tweetId,])
                rows = cursor.fetchall()
                print (rows)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows!= None):
                users=[]
                for row in rows:
                    tweetlike_dict={
                        "tweetId": row[0],
                        "userId" : row[1],
                        "username": row[2]
                    }
                    tweetlike_info.append(tweetlike_dict)
                return Response(json.dumps(tweetlike_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        tweetId=None
        createdAt=None
        tweetlike_info={}
        loginToken = request.json.get("loginToken")
        tweetId = request.json.get("tweetId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()           
            cursor.execute("SELECT * FROM user_session WHERE loginToken =?", [loginToken,])
            user=cursor.fetchall()
            print(user)
            if user !=None:
                cursor.execute("INSERT INTO tweet_like(tweetId, userId) VALUES(?,?)", [tweetId,user[0][0] ])
                conn.commit()
                rows= cursor.rowcount      
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows==1):
                return Response(json.dumps("tweet liked", default=str), mimetype="application/json", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        user = None
        loginToken = request.json.get("loginToken")
        tweetId = request.json.get("tweetId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken=?", [loginToken,])
            user = cursor.fetchone()
            print(user)
            if user !=None:
                cursor.execute("DELETE FROM tweet_like WHERE tweetId=? AND userId=?", [tweetId,user[0],])
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):           
                return Response(json.dumps("Deleted Successfully", default=str), mimetype="application/json", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

# USERS HAVE ABILITY TO LIKE COMMENTS AND UNLIKE COMMENTS THEY HAVE ALREADY LIKED 
@app.route('/api/comment-likes', methods=[ 'GET', 'POST', 'DELETE'])
def commentlikes():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        commentlike_info=[]
        commentlike_dict={}
        commentId = request.args.get("commentId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            if commentId != None and commentId != "":
                cursor.execute("SELECT c.commentId, c.userId, u.username FROM comment_like c INNER JOIN user u ON u.id = c.userId WHERE c.commentId = ?", [commentId,])
                rows = cursor.fetchall()
                print (rows)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows!= None):
                for row in rows:
                    commentlike_dict={
                        "commentId": row[0],
                        "userId" : row[1],
                        "username": row[2]
                    }
                    commentlike_info.append(commentlike_dict)
                return Response(json.dumps(commentlike_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        commentlike_info=[]
        commentlike_dict={}
        loginToken = request.json.get("loginToken")
        commentId = request.json.get("commentId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()           
            cursor.execute("SELECT * FROM user_session WHERE loginToken =?", [loginToken,])
            user=cursor.fetchall()
            print(user)
            if user !=None:
                cursor.execute("INSERT INTO comment_like(commentId, userId) VALUES(?,?)", [commentId,user[0][0] ])
                conn.commit()
                rows= cursor.rowcount      
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows==1):
                for row in rows:
                    commentlike_dict={
                        "commentId": row[0],
                        "userId" : row[1],
                        "username": row[2]
                    }
                    commentlike_info.append(commentlike_dict)
                return Response(json.dumps(commentlike_info, default=str), mimetype="application/json", status=201)

            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        user = None
        loginToken = request.json.get("loginToken")
        commentId = request.json.get("commentId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken=?", [loginToken,])
            user = cursor.fetchone()
            print(user)
            if user !=None:
                cursor.execute("DELETE FROM comment_like WHERE commentId=? AND userId=?", [commentId,user[0],])
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):           
                return Response(json.dumps("Comment deleted Successfully", default=str), mimetype="application/json", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
#Importing Libraries
import tweepy
from textblob import TextBlob
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import streamlit as st
from PIL import Image

#Import the configuration i.e keys saved from twitter developer account
#twitter access tokens
config = pd.read_csv('https://raw.githubusercontent.com/chinmayee521/Data/main/config.csv?token=AMJAJYRLTHHX2CVM76DCLDTA5ZPGU')

#retrieve all the individual keys
twitterApiKey = config['twitterApiKey'][0]
twitterApiSecret = config['twitterApiSecret'][0]
twitterApiAccessToken = config['twitterApiAccessToken'][0]
twitterApiAccessTokenSecret = config['twitterApiAccessTokenSecret'][0]

#Authenticate and set token using Tweepy
#Authenticate token using Tweepy
auth = tweepy.OAuthHandler(twitterApiKey, twitterApiSecret)
#Set access token
auth.set_access_token(twitterApiAccessToken, twitterApiAccessTokenSecret)
#Authenticate using tweepy api function
twitterApi = tweepy.API(auth, wait_on_rate_limit = True)

#Tweet Cleaning function
def cleanUpTweet(txt):
  #remove all the mentions using regular expression
  txt = re.sub(r'@[A-Za-z0-9_]+', '', txt)
  #remove hashtags
  txt = re.sub(r'#', '', txt)
  #remove retweets
  txt = re.sub(r'RT : ', '', txt)
  #remove urls
  txt = re.sub(r'https?:\/\/[A-Za-z0-9\.\/]+', '', txt)
  return txt

def getTextSubjectivity(txt):
  return TextBlob(txt).sentiment.subjectivity

def getTextPolarity(txt):
  return TextBlob(txt).sentiment.polarity

#polarity value < 0  -> negative sentiment
#polarity value = 0  -> neutral sentiment
#polarity value > 0  -> positive sentiment

#define a function for this

def getTextAnalysis(pol):
  if pol < 0:
    return "Negative"
  elif pol == 0:
    return "Neutral"
  else:
    return "Positive"

def app():
    st.title("Twitter Sentiment Analysis ✨" )
    st.sidebar.header("Twitter Sentiment Analysis")
    st.sidebar.write("Implemented using:")
    st.sidebar.write("- Python")
    st.sidebar.write("- StreamLit")
    st.sidebar.write("- Google Colaboratory")
    st.sidebar.write("- Tweepy python library (to access Twitter API)")
    st.sidebar.write("- TextBLOB (to process the tweets)")
    st.sidebar.subheader("Developed by: Chinmayee 💻")

    twitterAccount = st.text_area("Enter Twitter Username (without @)")
    choice = st.selectbox("Select your choice for Analysis",  ["Show Latest 10 Tweets", "Visualize the Sentiment Analysis", "Generate WordCloud", "Stats"])
    if st.button("Analyze"):
        #exclude replies, 50 tweets from twitter account will be retrieved in tweets
        tweets = tweepy.Cursor(twitterApi.user_timeline,
                            screen_name = twitterAccount,
                            count = None,
                            since_id = None,
                            max_id = None, trim_user = True, exclude_replies = True,
                            contributor_details = False,
                            include_entities = False).items(50);

        #takes all 50 tweets and forms a dataframe with column name Tweet
        df = pd.DataFrame(data = [tweet.text for tweet in tweets], columns = ['Tweet'])

        #apply cleanUpTweet function to all the tweets
        df['Tweet'] = df['Tweet'].apply(cleanUpTweet)

        #apply getTextSubjectivity and getTextPolarity functions to df

        #create new column Subjecivity in df
        df['Subjectivity'] = df['Tweet'].apply(getTextSubjectivity)

        #create new column Polarity in df
        df['Polarity'] = df['Tweet'].apply(getTextPolarity)

        #drop all columns having null tweets
        df = df.drop(df[df['Tweet']==''].index)

        df['Sentiment'] = df['Polarity'].apply(getTextAnalysis)



        if choice == "Show Latest 10 Tweets":
            st.info("Getting latest 10 Tweets")
            def Show10Tweets(twitterAccount):
                alltweets = twitterApi.user_timeline(screen_name = twitterAccount, count = 100, lang ="en", tweet_mode="extended")
                def get_10_tweets():
                    l=[]
                    i=1
                    for tweet in alltweets[:10]:
                        l.append(tweet.full_text)
                        i= i+1
                    return l

                latest_tweets = get_10_tweets()		
                return latest_tweets
            
            recent_tweets= Show10Tweets(twitterAccount)
            st.write(recent_tweets)
        
        elif choice == "Visualize the Sentiment Analysis":

            st.info("Generating Visualization for Sentiment Analysis")

            
            #calculate positive percentage
            positive = df[df['Sentiment']=='Positive']
            #print(str(positive.shape[0]/(df.shape[0])*100)+"% of positive tweets")
            pos = positive.shape[0]/df.shape[0]*100

            #calculate negative percentage
            negative = df[df['Sentiment']=='Negative']
            #print(str(negative.shape[0]/(df.shape[0])*100)+"% of negative tweets")
            neg = negative.shape[0]/df.shape[0]*100

            #calculate neutral percentage
            neutral = df[df['Sentiment']=='Neutral']
            #print(str(neutral.shape[0]/(df.shape[0])*100)+"% of neutral tweets")
            neu = neutral.shape[0]/df.shape[0]*100

            #Visualization using Pie Chart
            explode = (0,0.1,0)
            labels = '% Positive Tweets', '% Negative Tweets ', '% Neutral Tweets'
            sizes = [pos,neg,neu]
            colors = ['yellowgreen', 'lightcoral', 'gold']

            fig1, ax1 = plt.subplots()

            ax1.pie(sizes, explode = explode, labels = labels, colors = colors, autopct = '%1.1f%%', startangle = 120)
            ax1.axis('equal')
            ax1.set_title('Percentage Sentiment Analysis')
            st.pyplot(fig1)

            #Visualization using Bar Graph
            fig2, ax2 = plt.subplots()
            labels = df.groupby('Sentiment').count().index.values
            values = df.groupby('Sentiment').size().values
            barlist = ax2.bar(labels, values)
            ax2.set_title('Number of Tweets wrt to Sentiment')
            ax2.set_xlabel('Sentiment')
            ax2.set_ylabel('Count')
            barlist[0].set_color('lightcoral')
            barlist[2].set_color('yellowgreen')
            barlist[1].set_color('gold')
            st.pyplot(fig2)

        
        elif choice == "Generate WordCloud":

            st.info("Generating Word Cloud")

            # word cloud visualization
            allWords = ' '.join([twts for twts in df['Tweet']])
            wordCloud = WordCloud(width=500, height=300, random_state=21, max_font_size=110).generate(allWords)

            plt.imshow(wordCloud, interpolation="bilinear")
            plt.axis('off')
            plt.show()
            plt.axis('off')
            plt.savefig('Word cloud.jpg')
            img = Image.open("Word cloud.jpg")
            st.image(img)
        
        elif choice == "Stats":

            st.info("Loading Stats")

            st.header("Twitter Username: "+twitterAccount + "  Stats")

            values = df.groupby('Sentiment').size().values

            st.write(" ")
            st.write(" ")
            
            st.subheader("Number of Positive Tweets 😄 - "+ str(values[2]))
            #calculate positive percentage
            positive = df[df['Sentiment']=='Positive']
            p = "{:.2f}".format(positive.shape[0]/(df.shape[0])*100)
            st.subheader("% Positive Tweets - "+str(p)+"%")

            st.write(" ")

            st.subheader("Number of Negative Tweets 🙁 - "+ str(values[0]))
            #calculate negative percentage
            negative = df[df['Sentiment']=='Negative']
            ne = "{:.2f}".format(negative.shape[0]/(df.shape[0])*100)
            st.subheader("% Negative Tweets - "+str(ne)+"%")

            st.write(" ")

            st.subheader("Number of Neutral Tweets 😐 - "+ str(values[1]))
            #calculate neutral percentage
            neutral = df[df['Sentiment']=='Neutral']
            n = "{:.2f}".format(neutral.shape[0]/(df.shape[0])*100)
            st.subheader("% Neutral Tweets - "+str(n)+"%")

   


if __name__ == "__main__":
	app()
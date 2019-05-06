import requests
import re
from bs4 import BeautifulSoup
import csv
import json


class JavSpider(object):
	def __init__(self):
		self.headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.130 Safari/537.36 OPR/45.0.2257.46"
			}
		self.base_url = "https://www.javbus.com/actresses/{}"

	def get_all_actresses(self, index_url):
		response = requests.get(index_url, headers=self.headers)
		html = response.text
		soup = BeautifulSoup(html , "lxml")
		items = soup.find_all("a", class_="avatar-box text-center")
		actress_info = {}
		
		for item in items:
			actress_url = item["href"]
			actress_name = item.find("span").text
			actress_info[actress_name] = actress_url
		return actress_info


	def get_all_pages(self, actress_url):
		page_url_list = []
		index = 1
		while index < 20:
			actress_URL = actress_url + "/" + str(index)
			html = requests.get(actress_URL, headers=self.headers).text
			soup = BeautifulSoup(html, "lxml")
			alert = soup.find("div", class_="alert alert-danger alert-page error-page")
			if alert:
				break
			else:
				page_url_list.append(actress_URL)
				index += 1
		
		return page_url_list

	def get_onepage_movies(self, multiple_movies_url):
		response = requests.get(multiple_movies_url, headers=self.headers)
		if response.status_code == 200:
			html = response.text
			soup = BeautifulSoup(html, "lxml")
			items = soup.find_all("a", class_="movie-box")
			movie_url_list = []
			for item in items:
				movie_url = item["href"]
				movie_url_list.append(movie_url)

			return movie_url_list
		else:
			print(response.status_code, " error.")
			return None


	def get_movie_info(self, movie_url):
		response = requests.get(movie_url, headers=self.headers)
		if response.status_code == 200:
			html = response.text
			soup = BeautifulSoup(html, "lxml")
			movie_detailed_info = {}
			Title = soup.find("h3").text
			info_block = soup.find("div", class_="col-md-3 info").find_all("p")
			UUID = info_block[0].find_all("span")[-1].text
			Release_Time = info_block[1].contents[-1]
			try:
				Duration = info_block[2].contents[-1]
			except:
				Duration = None
			try:
				Director = info_block[3].find("a").text
			except:
				Director = None
			try:
				Producer = info_block[4].find("a").text
			except:
				Producer = None
			try:
				Issurer = info_block[5].find("a").text
			except:
				Issurer = None
			try:
				Type_Series = info_block[6].find("a").text
			except:
				Type_Series = None
			try:
				Actress = []
				actress_list = info_block[-1].find_all("a")
				for actress in actress_list:
					Actress.append(actress.text)
			except:
				Actress = ["None"]

			movie_detailed_info["Title"] = Title
			movie_detailed_info["UUID"] = UUID
			movie_detailed_info["Release_Time"] = Release_Time
			movie_detailed_info["Duration"] = Duration
			movie_detailed_info["Director"] = Director
			movie_detailed_info["Producer"] = Producer
			movie_detailed_info["Issurer"] = Issurer
			movie_detailed_info["Type_Series"] = Type_Series
			movie_detailed_info["Actress"] = Actress
			
			# Get magnet url
			pattern1 = re.compile("gid = (.*?);", re.S)
			pattern2 = re.compile("var img = '(.*?)';", re.S)
			gid_value = re.search(pattern1, html).group(1)
			img_url = re.search(pattern2, html).group(1)
			headers = {
				"referer": movie_url,
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.130 Safari/537.36 OPR/45.0.2257.46"
			}
			magnet_ajax_url = "https://www.javbus.com/ajax/uncledatoolsbyajax.php?gid={}&lang=zh&img={}&uc=0".format(gid_value, img_url)
			ajax_response = requests.get(magnet_ajax_url, headers=headers)
			soup = BeautifulSoup(ajax_response.text, "lxml")
			magnet_url_list = []
			try:
				for magnet_url in soup.select('td[width="70%"]'):
					magnet_url_list.append(magnet_url.a['href'])
				movie_detailed_info["Magnet"] = magnet_url_list
			except:
				movie_detailed_info["Magnet"] = magnet_url_list
			
			movie_detailed_info["Img"] = img_url
			
			print(movie_detailed_info["Title"])
			with open("JavbusMovieInfo.csv", "a", encoding="UTF-8") as csvfile:
				writer = csv.writer(csvfile)
				writer.writerow([Title, UUID, Release_Time, Duration, Director, Producer, Issurer, Type_Series, Actress, magnet_url_list, img_url])
		else:
			print(response.status_code, " detailed page error.")

	def RunSpider(self):
		start_page = input("start page:")
		end_page = input("end page:")
		for i in range(int(start_page), int(end_page)+1):
			index_url = self.base_url.format(i)
			actress_info = self.get_all_actresses(index_url)
			for actress_url in actress_info.values():
				page_url_list = self.get_all_pages(actress_url)
				for multiple_movies_url in page_url_list:
					print(multiple_movies_url)
					movie_url_list = self.get_onepage_movies(multiple_movies_url)
					for movie_url in movie_url_list:
						self.get_movie_info(movie_url)
			
if __name__ == "__main__":
	JavSpider = JavSpider()
	JavSpider.RunSpider()
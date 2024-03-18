import folium
import webbrowser
import os
import time
import subprocess

#with the help of Github Copilot
class Map:

  def __init__(self, entrylist, start_x, start_y, zoom):
    self.entrylist = entrylist
    self.x = start_x
    self.y = start_y
    self.zoom = zoom

  def add_entry(self, entry):
    self.entrylist.append(entry)

  def update_html(self):
    m = folium.Map(location=[self.x, self.y], zoom_start=self.zoom)
    for entry in self.entrylist:
      self.poptext = "{}:{}".format(entry['id'], entry['title'])
      folium.CircleMarker(location=[int(entry["lat"]),
                                    int(entry["long"])],
                          radius=entry["radius"],
                          color=None,
                          fill=True,
                          fill_color=entry["type"],
                          fill_opacity=entry["transparency"],
                          popup=folium.Popup(self.poptext)).add_to(m)
    m.save('map.html')

  def run(self):#with the help of ai
    server_process = subprocess.Popen(["python3", "-m", "http.server", "8080"])

        # Wait for a few seconds to ensure the server has started
    time.sleep(3)
        # Open the HTML file in the preview browser
    os.system("xdg-open http://localhost:8080/map.html &")
    input("Press Enter to stop the server...")
    # Terminate the server process
    server_process.terminate()


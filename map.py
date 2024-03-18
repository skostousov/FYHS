import folium
import webbrowser

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
      folium.CircleMarker(
          location=[int(entry["lat"]), int(entry["long"])],
          radius=entry["radius"],
          color=None,
          fill=True,
          fill_color=entry["type"],
          fill_opacity=entry["transparency"],
          popup=folium.Popup(f"{entry['id']}:{entry['title']}"),#ai advice utilized
      ).add_to(m)
    m.save('map.html')

  def run(self):
    import os
    os.system("start chrome map.html")



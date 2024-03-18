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
    webbrowser.open('map.html')

# mapinstance = Map([
#   {"latitude": 40.7128, "longitude": -74.0060, "radius": 5, "color": "red", "opacity": 0.6},
#   {"latitude": 40.7589, "longitude": -73.9851, "radius": 3, "color": "blue", "opacity": 0.8},
#   {"latitude": 40.6782, "longitude": -73.9442, "radius": 4, "color": "green", "opacity": 0.7},
#   {"latitude": 40.7291, "longitude": -73.9965, "radius": 5, "color": "yellow", "opacity": 0.5},
#   {"latitude": 40.7421, "longitude": -74.0049, "radius": 6, "color": "orange", "opacity": 0.4},
#   {"latitude": 40.7679, "longitude": -73.9822, "radius": 7, "color": "purple", "opacity": 0.3}
# ])
# mapinstance.update_html()
# mapinstance.run()

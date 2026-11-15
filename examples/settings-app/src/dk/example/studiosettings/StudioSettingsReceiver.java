package dk.example.studiosettings;
import android.content.*;
import org.json.*;
import studio.settings.StudioSettingsBridge;

public class StudioSettingsReceiver extends StudioSettingsBridge {
 protected JSONObject readValues(Context context, JSONObject schema) throws Exception {
  JSONObject saved=new JSONObject(context.getSharedPreferences("example",0).getString("settings","{}")),values=new JSONObject();
  JSONArray fields=schema.getJSONArray("fields");
  for(int i=0;i<fields.length();i++){JSONObject field=fields.getJSONObject(i);String key=field.getString("key");values.put(key,saved.has(key)?saved.get(key):field.get("default"));}
  return values;
 }
 protected void applyValues(Context context, JSONObject values) throws Exception {
  if(!context.getSharedPreferences("example",0).edit().putString("settings",values.toString()).commit())throw new Exception("Settings not saved");
  // Notify your own runtime here after validation and durable saving.
 }
}

package dk.example.studiosettings;
import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;
public class MainActivity extends Activity {
 public void onCreate(Bundle state){super.onCreate(state);TextView label=new TextView(this);label.setText("Studio settings API 1 example\nSelect this app in Studio to edit its settings.");label.setTextSize(24);label.setPadding(32,32,32,32);setContentView(label);}
}

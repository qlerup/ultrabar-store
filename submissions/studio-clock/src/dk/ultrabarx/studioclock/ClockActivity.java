package dk.ultrabarx.studioclock;
import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/** Offline clock: device-local date/time, no services or permissions. */
public class ClockActivity extends Activity {
 private final Handler handler=new Handler();
 private TextView clock,date;
 private final Runnable tick=new Runnable(){ public void run(){
  Date now=new Date();
  clock.setText(new SimpleDateFormat("HH:mm:ss",Locale.getDefault()).format(now));
  date.setText(new SimpleDateFormat("EEEE, d MMMM yyyy",Locale.getDefault()).format(now));
  handler.postDelayed(this,1000-System.currentTimeMillis()%1000);
 }};
 @Override public void onCreate(Bundle state){super.onCreate(state);
  getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
  LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setGravity(Gravity.CENTER);root.setBackgroundColor(0xff101116);root.setPadding(20,8,20,8);
  clock=new TextView(this);clock.setTextColor(0xfff0f1f8);clock.setTextSize(76);clock.setGravity(Gravity.CENTER);clock.setFontFeatureSettings("tnum");
  date=new TextView(this);date.setTextColor(0xffb9b2ff);date.setTextSize(24);date.setGravity(Gravity.CENTER);
  root.addView(clock);root.addView(date);setContentView(root);
 }
 @Override protected void onResume(){super.onResume();handler.removeCallbacks(tick);tick.run();}
 @Override protected void onPause(){handler.removeCallbacks(tick);super.onPause();}
}

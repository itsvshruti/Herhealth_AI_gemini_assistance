import streamlit as st
import pandas as pd
from datetime import date, timedelta
from google import genai
from google.genai import types

st.set_page_config(page_title="HerHealth AI", page_icon="🌷", layout="wide")

# -------------------- Language support --------------------
TEXT = {
"English": {
"tagline":"Your health. Your journey. Your wellbeing.",
"disclaimer":"Educational information only. HerHealth AI does not diagnose, prescribe, predict pregnancy complications or replace a qualified healthcare professional. For urgent or severe symptoms, contact local emergency services or a healthcare professional promptly.",
"language":"Choose language",
"home":"Home","preg":"Pregnancy Care","pcos":"PCOS Care","assistant":"AI Health Assistant","planner":"My Health Planner","resources":"Resources",
"welcome":"A gentle space for every stage of your health journey.",
"intro":"Explore pregnancy education, understand PCOS, organize appointments and ask general health questions in simple language.",
"preg_title":"Pregnancy Care","preg_desc":"Understand your estimated pregnancy timeline and organize appointments recommended by your maternity-care team.",
"lmp":"First day of your last menstrual period (LMP)","estimate":"Your estimated timeline","weeks":"Estimated pregnancy stage","due":"Estimated due date","days":"Days since LMP",
"lmp_note":"This is a simple estimate based on 280 days from LMP and assumes a 28-day cycle. Actual dating can vary. A clinician may revise the estimate using your history and ultrasound.",
"appointments":"Appointment planner","appointment_date":"Appointment date","appointment_type":"Appointment type","notes":"Notes (optional)","add":"Add appointment","saved":"Appointment added to this session.","no_appointments":"No appointments added yet.","appointment_help":"Add appointments and tests recommended by your own doctor or midwife. This is an organizer, not a medical schedule.",
"pcos_title":"PCOS Care & Cycle Journal","pcos_desc":"Learn about PCOS and keep a personal record of cycle changes and symptoms. A journal cannot diagnose PCOS.",
"cycle_date":"Date","cycle_note":"Cycle / bleeding note","symptoms":"What did you notice?","save":"Save journal entry","journal_saved":"Journal entry saved for this session.","no_entries":"Your journal is empty.","pcos_info":"PCOS is a common hormonal condition that can affect menstrual cycles, skin, hair and metabolism. Symptoms vary. Diagnosis requires an assessment by a qualified clinician; symptoms alone are not enough.",
"wellbeing":"General wellbeing topics to discuss with your clinician","wellbeing_text":"• Regular, sustainable movement that suits your health and ability.\\n• Balanced eating patterns that are practical and culturally appropriate.\\n• Sleep and emotional wellbeing.\\n• Track cycle changes and concerns for your appointment.\\n• Ask whether blood pressure, glucose, cholesterol or other checks are appropriate for you.",
"ai_title":"AI Women's Health Explainer","ai_desc":"Ask general educational questions about pregnancy, PCOS or women's health. Do not use this tool for diagnosis or urgent medical advice.",
"question":"Your question","ask":"Ask HerHealth AI","api":"Gemini API key (optional)","model":"AI model","api_help":"Your Gemini key is used for this session. Never share it or commit it to GitHub.",
"ai_empty":"Please enter a question.","api_missing":"Enter a Gemini API key in the sidebar to use the AI explainer.","answer":"HerHealth AI says","ai_note":"AI-generated information can be incomplete or inaccurate. Confirm personal health decisions with a qualified clinician.",
"planner_title":"My Health Planner","planner_desc":"Keep your appointment list and health journal organized. Entries are held only in this active app session and are not a permanent medical record.",
"download":"Download CSV","resources_title":"Trusted health resources","resource_note":"Guidelines and local care pathways can change. Check current local guidance and discuss personal care with your clinician.",
"footer":"HerHealth AI • Women's health education prototype • Not a medical device",
"preg_types":["Antenatal consultation","Blood pressure / urine check","Blood test (as advised)","Ultrasound / scan (as advised)","Nutrition discussion","Other"],
"cycle_types":["Period started","Period ended","Spotting","No bleeding / cycle not started","Prefer not to say"],
"symptom_types":["Acne","Increased facial/body hair","Hair thinning","Pelvic discomfort","Mood changes","Sleep difficulty","Fatigue","Other"],
"appointment":"Appointment","complete":"Completed","period":"Period started","symptom":"Symptoms","journal":"Cycle journal",
},
"Hindi": {
"tagline":"आपका स्वास्थ्य। आपकी यात्रा। आपका ख्याल।",
"disclaimer":"यह जानकारी केवल शैक्षिक उद्देश्य के लिए है। HerHealth AI बीमारी का निदान, दवा की सलाह या गर्भावस्था की जटिलताओं की भविष्यवाणी नहीं करता और डॉक्टर का विकल्प नहीं है। गंभीर या आपातकालीन लक्षण होने पर तुरंत स्थानीय आपातकालीन सेवा या स्वास्थ्य विशेषज्ञ से संपर्क करें।",
"language":"भाषा चुनें","home":"होम","preg":"गर्भावस्था देखभाल","pcos":"PCOS देखभाल","assistant":"AI स्वास्थ्य सहायक","planner":"मेरा स्वास्थ्य प्लानर","resources":"संसाधन",
"welcome":"आपकी स्वास्थ्य यात्रा के हर चरण के लिए एक सहायक जगह।","intro":"गर्भावस्था की जानकारी देखें, PCOS को समझें, अपॉइंटमेंट व्यवस्थित करें और सरल भाषा में सामान्य स्वास्थ्य प्रश्न पूछें।",
"preg_title":"गर्भावस्था देखभाल","preg_desc":"गर्भावस्था की अनुमानित अवधि समझें और डॉक्टर द्वारा सुझाए गए अपॉइंटमेंट व्यवस्थित करें।",
"lmp":"अंतिम मासिक धर्म का पहला दिन (LMP)","estimate":"आपकी अनुमानित समय-रेखा","weeks":"अनुमानित गर्भावस्था अवधि","due":"अनुमानित प्रसव तिथि","days":"LMP के बाद के दिन",
"lmp_note":"यह LMP से 280 दिनों पर आधारित एक सरल अनुमान है और 28-दिन के चक्र को मानता है। वास्तविक अवधि अलग हो सकती है। डॉक्टर आपकी जानकारी और अल्ट्रासाउंड के आधार पर इसे बदल सकते हैं।",
"appointments":"अपॉइंटमेंट प्लानर","appointment_date":"अपॉइंटमेंट की तारीख","appointment_type":"अपॉइंटमेंट का प्रकार","notes":"नोट्स (वैकल्पिक)","add":"अपॉइंटमेंट जोड़ें","saved":"इस सत्र में अपॉइंटमेंट जोड़ दिया गया।","no_appointments":"अभी कोई अपॉइंटमेंट नहीं जोड़ा गया।","appointment_help":"अपने डॉक्टर या मिडवाइफ द्वारा सुझाए गए अपॉइंटमेंट और जांच जोड़ें। यह केवल आयोजक है, मेडिकल शेड्यूल नहीं।",
"pcos_title":"PCOS देखभाल और मासिक चक्र डायरी","pcos_desc":"PCOS के बारे में जानें और मासिक चक्र तथा लक्षणों का रिकॉर्ड रखें। डायरी से PCOS का निदान नहीं किया जा सकता।",
"cycle_date":"तारीख","cycle_note":"मासिक चक्र / रक्तस्राव नोट","symptoms":"आपने क्या अनुभव किया?","save":"डायरी सेव करें","journal_saved":"इस सत्र में डायरी सेव हो गई।","no_entries":"आपकी डायरी खाली है।",
"pcos_info":"PCOS एक हार्मोन संबंधी स्थिति है जो मासिक चक्र, त्वचा, बालों और मेटाबॉलिज्म को प्रभावित कर सकती है। लक्षण अलग-अलग होते हैं। निदान के लिए योग्य डॉक्टर का मूल्यांकन आवश्यक है; केवल लक्षण पर्याप्त नहीं हैं।",
"wellbeing":"डॉक्टर से चर्चा करने योग्य सामान्य स्वास्थ्य विषय","wellbeing_text":"• अपनी क्षमता के अनुसार नियमित और सुरक्षित शारीरिक गतिविधि।\\n• संतुलित और व्यवहारिक भोजन।\\n• पर्याप्त नींद और भावनात्मक स्वास्थ्य।\\n• अपॉइंटमेंट के लिए मासिक चक्र में बदलाव नोट करें।\\n• डॉक्टर से पूछें कि आपके लिए ब्लड प्रेशर, ग्लूकोज़, कोलेस्ट्रॉल या अन्य जांच आवश्यक हैं या नहीं।",
"ai_title":"AI महिला स्वास्थ्य जानकारी सहायक","ai_desc":"गर्भावस्था, PCOS या महिला स्वास्थ्य के बारे में सामान्य जानकारी पूछें। इसका उपयोग निदान या आपातकालीन सलाह के लिए न करें।",
"question":"आपका प्रश्न","ask":"HerHealth AI से पूछें","api":"Gemini API key (वैकल्पिक)","model":"AI मॉडल","api_help":"आपकी Gemini key केवल इस सत्र में उपयोग होती है। इसे साझा न करें या GitHub पर अपलोड न करें।",
"ai_empty":"कृपया प्रश्न लिखें।","api_missing":"AI explainer के लिए sidebar में Gemini API key डालें।","answer":"HerHealth AI का उत्तर","ai_note":"AI की जानकारी अधूरी या गलत हो सकती है। व्यक्तिगत स्वास्थ्य निर्णय डॉक्टर से पुष्टि करें।",
"planner_title":"मेरा स्वास्थ्य प्लानर","planner_desc":"अपॉइंटमेंट और स्वास्थ्य डायरी व्यवस्थित रखें। जानकारी केवल सक्रिय ऐप सत्र में रहती है, स्थायी मेडिकल रिकॉर्ड नहीं है।",
"download":"CSV डाउनलोड करें","resources_title":"विश्वसनीय स्वास्थ्य संसाधन","resource_note":"दिशानिर्देश और स्थानीय स्वास्थ्य सेवाएं बदल सकती हैं। वर्तमान स्थानीय जानकारी देखें और डॉक्टर से सलाह लें।",
"footer":"HerHealth AI • महिला स्वास्थ्य शिक्षा प्रोटोटाइप • मेडिकल डिवाइस नहीं",
"preg_types":["गर्भावस्था परामर्श","ब्लड प्रेशर / यूरिन जांच","ब्लड टेस्ट (सलाह अनुसार)","अल्ट्रासाउंड / स्कैन (सलाह अनुसार)","पोषण परामर्श","अन्य"],
"cycle_types":["पीरियड शुरू हुआ","पीरियड समाप्त हुआ","हल्का रक्तस्राव","रक्तस्राव नहीं / चक्र शुरू नहीं हुआ","नहीं बताना चाहती/चाहता"],
"symptom_types":["मुंहासे","चेहरे/शरीर पर अधिक बाल","बाल पतले होना","पेल्विक असुविधा","मूड में बदलाव","नींद में परेशानी","थकान","अन्य"],
"appointment":"अपॉइंटमेंट","complete":"पूरा हुआ","period":"पीरियड शुरू हुआ","symptom":"लक्षण","journal":"मासिक चक्र डायरी",
},
"Marathi": {
"tagline":"तुमचे आरोग्य. तुमचा प्रवास. तुमची काळजी.",
"disclaimer":"ही माहिती केवळ शैक्षणिक उद्देशासाठी आहे. HerHealth AI निदान करत नाही, औषधे सुचवत नाही, गर्भधारणेतील गुंतागुंत भाकीत करत नाही आणि डॉक्टरांचा पर्याय नाही. गंभीर किंवा तातडीची लक्षणे असल्यास त्वरित स्थानिक आपत्कालीन सेवा किंवा आरोग्यतज्ज्ञांशी संपर्क साधा.",
"language":"भाषा निवडा","home":"मुख्यपृष्ठ","preg":"गर्भधारणा काळजी","pcos":"PCOS काळजी","assistant":"AI आरोग्य सहाय्यक","planner":"माझे आरोग्य नियोजक","resources":"संसाधने",
"welcome":"तुमच्या आरोग्य प्रवासातील प्रत्येक टप्प्यासाठी एक मदतीची जागा.","intro":"गर्भधारणेची माहिती जाणून घ्या, PCOS समजून घ्या, भेटींचे नियोजन करा आणि सोप्या भाषेत सामान्य आरोग्यविषयक प्रश्न विचारा.",
"preg_title":"गर्भधारणा काळजी","preg_desc":"गर्भधारणेचा अंदाजित कालावधी समजून घ्या आणि डॉक्टरांनी सुचवलेल्या भेटींचे नियोजन करा.",
"lmp":"शेवटच्या मासिक पाळीचा पहिला दिवस (LMP)","estimate":"तुमचा अंदाजित कालावधी","weeks":"अंदाजित गर्भधारणेचा टप्पा","due":"अंदाजित प्रसूती तारीख","days":"LMP नंतरचे दिवस",
"lmp_note":"हा LMP पासून 280 दिवसांवर आधारित साधा अंदाज आहे आणि 28 दिवसांचे चक्र गृहीत धरतो. प्रत्यक्ष कालावधी वेगळा असू शकतो. डॉक्टर वैद्यकीय माहिती आणि सोनोग्राफीच्या आधारे तारीख बदलू शकतात.",
"appointments":"भेटींचे नियोजन","appointment_date":"भेटीची तारीख","appointment_type":"भेटीचा प्रकार","notes":"नोंदी (ऐच्छिक)","add":"भेट जोडा","saved":"या सत्रात भेट जोडली आहे.","no_appointments":"अजून कोणतीही भेट जोडलेली नाही.","appointment_help":"तुमच्या डॉक्टरांनी किंवा मिडवाइफने सुचवलेल्या भेटी आणि तपासण्या जोडा. हे फक्त नियोजनासाठी आहे; वैद्यकीय वेळापत्रक नाही.",
"pcos_title":"PCOS काळजी आणि मासिक पाळी नोंदवही","pcos_desc":"PCOS बद्दल जाणून घ्या आणि मासिक पाळीतील बदल व लक्षणांची नोंद ठेवा. नोंदवहीवरून PCOS चे निदान होत नाही.",
"cycle_date":"तारीख","cycle_note":"मासिक पाळी / रक्तस्राव नोंद","symptoms":"तुम्हाला काय जाणवले?","save":"नोंद जतन करा","journal_saved":"या सत्रात नोंद जतन झाली.","no_entries":"तुमची नोंदवही रिकामी आहे.",
"pcos_info":"PCOS ही हार्मोन्सशी संबंधित स्थिती आहे. तिचा मासिक पाळी, त्वचा, केस आणि चयापचयावर परिणाम होऊ शकतो. लक्षणे प्रत्येक व्यक्तीत वेगळी असतात. निदानासाठी पात्र डॉक्टरांचे मूल्यांकन आवश्यक आहे; केवळ लक्षणे पुरेशी नाहीत.",
"wellbeing":"डॉक्टरांशी चर्चा करण्यासारखे सामान्य आरोग्य विषय","wellbeing_text":"• तुमच्या क्षमतेनुसार नियमित आणि सुरक्षित हालचाल.\\n• संतुलित आणि व्यवहार्य आहार.\\n• पुरेशी झोप आणि भावनिक आरोग्य.\\n• भेटीसाठी मासिक पाळीतील बदल नोंदवा.\\n• तुमच्यासाठी रक्तदाब, ग्लुकोज, कोलेस्टेरॉल किंवा इतर तपासण्या आवश्यक आहेत का ते डॉक्टरांना विचारा.",
"ai_title":"AI महिला आरोग्य माहिती सहाय्यक","ai_desc":"गर्भधारणा, PCOS किंवा महिला आरोग्याबद्दल सामान्य माहिती विचारा. निदान किंवा आपत्कालीन सल्ल्यासाठी याचा वापर करू नका.",
"question":"तुमचा प्रश्न","ask":"HerHealth AI ला विचारा","api":"Gemini API key (ऐच्छिक)","model":"AI मॉडेल","api_help":"तुमची Gemini key फक्त या सत्रात वापरली जाते. ती शेअर करू नका किंवा GitHub वर अपलोड करू नका.",
"ai_empty":"कृपया प्रश्न लिहा.","api_missing":"AI explainer वापरण्यासाठी sidebar मध्ये Gemini API key द्या.","answer":"HerHealth AI चे उत्तर","ai_note":"AI माहिती अपूर्ण किंवा चुकीची असू शकते. वैयक्तिक आरोग्य निर्णय डॉक्टरांकडून तपासून घ्या.",
"planner_title":"माझे आरोग्य नियोजक","planner_desc":"भेटी आणि आरोग्य नोंदी व्यवस्थित ठेवा. माहिती फक्त सध्याच्या अॅप सत्रात राहते; हा कायमस्वरूपी वैद्यकीय रेकॉर्ड नाही.",
"download":"CSV डाउनलोड करा","resources_title":"विश्वसनीय आरोग्य संसाधने","resource_note":"मार्गदर्शक तत्त्वे आणि स्थानिक आरोग्य सेवा बदलू शकतात. अद्ययावत स्थानिक माहिती तपासा आणि डॉक्टरांचा सल्ला घ्या.",
"footer":"HerHealth AI • महिला आरोग्य शिक्षण प्रोटोटाइप • वैद्यकीय उपकरण नाही",
"preg_types":["गर्भधारणा सल्लामसलत","रक्तदाब / लघवी तपासणी","रक्त तपासणी (सल्ल्यानुसार)","सोनोग्राफी / स्कॅन (सल्ल्यानुसार)","आहार सल्ला","इतर"],
"cycle_types":["मासिक पाळी सुरू झाली","मासिक पाळी संपली","थोडा रक्तस्राव","रक्तस्राव नाही / पाळी सुरू नाही","सांगू इच्छित नाही"],
"symptom_types":["मुरुम","चेहरा/शरीरावर जास्त केस","केस पातळ होणे","ओटीपोटात अस्वस्थता","मूडमध्ये बदल","झोपेची अडचण","थकवा","इतर"],
"appointment":"भेट","complete":"पूर्ण झाले","period":"मासिक पाळी सुरू झाली","symptom":"लक्षणे","journal":"मासिक पाळी नोंदवही",
}
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
:root {
  --lavender:#8b6a9d; --deep:#5b426b; --rose:#d88fa7;
  --peach:#f4c5b2; --ink:#493d4c; --muted:#786b7c;
}
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {
  background:
    radial-gradient(circle at 8% 4%,rgba(232,211,244,.48),transparent 26rem),
    radial-gradient(circle at 92% 16%,rgba(255,222,210,.48),transparent 25rem),
    linear-gradient(180deg,#fcf9fd 0%,#fffaf8 52%,#fbf8fc 100%);
  color:var(--ink);
}
.block-container {max-width:1160px;padding-top:1.1rem;padding-bottom:3rem;}
#MainMenu, footer {visibility:hidden;}
header[data-testid="stHeader"] {background:transparent;}
.hero {
  position:relative; overflow:hidden;
  background:linear-gradient(115deg,#eee4f5 0%,#f9e9ef 52%,#ffede3 100%);
  padding:56px 42px;border-radius:30px;border:1px solid #f0e4f0; min-height:330px;
  background-image:linear-gradient(90deg,rgba(248,239,250,.98) 0%,rgba(249,235,242,.93) 48%,rgba(249,235,242,.15) 100%),url("https://images.unsplash.com/photo-1512290923902-8a9f81dc236c?auto=format&fit=crop&w=1400&q=85");
  background-position:center,right center;background-size:cover;
  margin:4px 0 22px; box-shadow:0 12px 35px rgba(105,76,119,.08);
}
.hero:after {
  content:"✿"; position:absolute; right:42px; top:-22px;
  font-size:132px; color:rgba(255,255,255,.58); transform:rotate(14deg);
}
.hero h1 {
  font-family:'Playfair Display',serif!important;
  font-size:clamp(2.25rem,5vw,3.25rem)!important;
  color:#624a70!important; margin:0!important; font-weight:700!important;
  letter-spacing:-1px;
}
.hero p {font-size:1.08rem;color:#765e76;margin:9px 0 0;max-width:650px;}
.hero .hero-kicker {font-size:.78rem;text-transform:uppercase;letter-spacing:2px;color:#946f91;font-weight:700;margin-bottom:9px;}
h1,h2,h3 {color:#604b70!important;}
h1,h2 {font-family:'Playfair Display',serif!important;}
h2 {font-size:1.8rem!important;}
h3 {font-size:1.12rem!important;}
p, label, .stMarkdown {color:var(--ink);}
div[data-testid="stAlert"] {border-radius:16px;border:1px solid #eee2ef;background:#fffafd;}
div[data-testid="stMetric"] {
  background:linear-gradient(145deg,#fff 0%,#fcf7fd 100%);
  border:1px solid #eee2f1;padding:18px 19px;border-radius:20px;
  box-shadow:0 5px 18px rgba(91,66,107,.045);
}
div[data-testid="stMetricLabel"] {color:#806c88;}
div[data-testid="stMetricValue"] {color:#624a70;font-weight:700;}
.stTabs [data-baseweb="tab-list"] {
  gap:8px;background:rgba(255,255,255,.78);padding:8px;
  border:1px solid #f0e6f1;border-radius:18px;margin:8px 0 22px;
}
.stTabs [data-baseweb="tab"] {
  background:transparent;border-radius:12px;padding:11px 15px;
  color:#76657d;font-weight:600;transition:all .2s ease;
}
.stTabs [aria-selected="true"] {background:#eee4f4!important;color:#624a70!important;}
.stTabs [data-baseweb="tab-highlight"] {background:#9b7aaa;height:3px;}
.stButton>button, .stDownloadButton>button, button[kind="primary"] {
  border-radius:14px;border:1px solid #8f72a6;
  background:linear-gradient(110deg,#8f72a6,#a27fac);
  color:white;font-weight:700;padding:.58rem 1.1rem;
  box-shadow:0 5px 14px rgba(143,114,166,.16);transition:all .18s ease;
}
.stButton>button:hover, .stDownloadButton>button:hover {
  background:linear-gradient(110deg,#735985,#8b6a9d);color:white;
  border-color:#735985;transform:translateY(-1px);
}
div[data-testid="stForm"] {
  background:rgba(255,255,255,.88);border:1px solid #eee3ef;
  padding:20px;border-radius:20px;box-shadow:0 7px 22px rgba(91,66,107,.04);
}
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea,
div[data-testid="stDateInput"] input, div[data-testid="stSelectbox"] [data-baseweb="select"] {
  border-radius:12px!important;border-color:#e8dce9!important;background:#fff!important;
}
div[data-testid="stMultiSelect"] [data-baseweb="select"] {border-radius:12px!important;}
[data-testid="stSidebar"] {
  background:linear-gradient(180deg,#f4edf8 0%,#fff3ef 100%);
  border-right:1px solid #eee2ef;
}
[data-testid="stSidebar"] h2 {font-family:'Playfair Display',serif!important;color:#624a70!important;}
[data-testid="stExpander"] {border:1px solid #eee2ef;border-radius:15px;background:#fff;}
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
  border:1px solid #eee3ef;border-radius:16px;overflow:hidden;
}
.feature-photo {width:100%;height:172px;object-fit:cover;border-radius:17px;margin-bottom:16px;display:block;background:#f7e8ef;}
.section-eyebrow {font-size:.78rem;letter-spacing:2px;text-transform:uppercase;color:#a1769c;font-weight:700;margin:20px 0 8px;}
.trust-strip {display:flex;flex-wrap:wrap;gap:12px;margin:20px 0 25px;}
.trust-pill {padding:10px 15px;border:1px solid #eddfeb;background:#fff;border-radius:100px;font-size:.83rem;color:#765b7e;}
.card {
  background:rgba(255,255,255,.88);border:1px solid #eee3ef;
  border-radius:22px;padding:22px 20px;height:100%;
  box-shadow:0 8px 24px rgba(91,66,107,.055);
  transition:transform .2s ease,box-shadow .2s ease;
}
.card:hover {transform:translateY(-3px);box-shadow:0 12px 28px rgba(91,66,107,.10);}
.card .card-icon {font-size:1.8rem;margin-bottom:9px;}
.card h3 {margin:0 0 8px!important;color:#624a70!important;}
.card p {color:#786b7c;font-size:.94rem;line-height:1.55;margin:0;}
.home-intro {
  background:rgba(255,255,255,.62);border:1px solid #f0e6f1;
  border-radius:20px;padding:20px 23px;margin:8px 0 20px;
}
.soft-note {
  background:linear-gradient(110deg,#f4edf8,#fff0e9);border:1px solid #eee2ef;
  border-radius:18px;padding:17px 20px;color:#6f5b77;
}
hr {border-color:#eee4ef!important;}
.stCaption, small {color:var(--muted)!important;}
@media (max-width: 760px) {
  .block-container {padding-left:1rem;padding-right:1rem;}
  .hero {padding:26px 22px;border-radius:22px;}
  .hero:after {right:12px;font-size:88px;top:-8px;}
  .stTabs [data-baseweb="tab"] {padding:9px 10px;font-size:.82rem;}
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🌷 HerHealth AI")
    lang = st.selectbox("Language / भाषा / भाषा", ["English","Hindi","Marathi"], index=0)
    try:
        saved_gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        saved_gemini_key = ""
    api_key = st.text_input(TEXT[lang]["api"], value=saved_gemini_key, type="password", help=TEXT[lang]["api_help"])
    model = st.selectbox(TEXT[lang]["model"], ["gemini-3.5-flash-lite"], help="Google Gemini API free-tier model; availability and quotas can change.")
    st.caption("🔒 Avoid entering names, phone numbers, addresses or identifiable medical details.")

t = TEXT[lang]
st.markdown(f'<div class="hero"><div class="hero-kicker">A softer space for women’s wellbeing</div><h1>🌷 HerHealth AI</h1><p>{t["tagline"]}</p></div>', unsafe_allow_html=True)
st.warning(t["disclaimer"])

tabs = st.tabs([f"🏡 {t['home']}",f"🤰 {t['preg']}",f"🌸 {t['pcos']}",f"💬 {t['assistant']}",f"🗓️ {t['planner']}",f"📚 {t['resources']}"])

if "visits" not in st.session_state: st.session_state.visits=[]
if "logs" not in st.session_state: st.session_state.logs=[]

with tabs[0]:
    st.markdown(f'<div class="home-intro"><h2>{t["welcome"]}</h2><p>{t["intro"]}</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="section-eyebrow">EXPLORE YOUR WELLNESS SPACE</div>', unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1:
        st.markdown('<div class="card"><img class="feature-photo" src="https://images.unsplash.com/photo-1491013516836-7db643ee125a?auto=format&fit=crop&w=700&q=80" alt="Mother and baby"/><div class="card-icon">🤰🏻</div><h3>Pregnancy Care</h3><p>A calm place to view an estimated timeline, organize appointments and keep helpful notes for your care team.</p></div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><img class="feature-photo" src="https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=700&q=80" alt="Woman practicing yoga"/><div class="card-icon">🌷</div><h3>PCOS & Cycle Journal</h3><p>Learn at your own pace and keep track of cycle changes and symptoms in one simple journal.</p></div>',unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card"><img class="feature-photo" src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=700&q=80" alt="Healthcare consultation"/><div class="card-icon">💗</div><h3>AI Health Explainer</h3><p>Explore general women’s-health topics with clear, supportive explanations in your preferred language.</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="trust-strip"><span class="trust-pill">✦ English · हिन्दी · मराठी</span><span class="trust-pill">♡ Gentle, judgment-free design</span><span class="trust-pill">✧ Private session-only journal</span><span class="trust-pill">✓ Educational support, not diagnosis</span></div>',unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="soft-note"><strong>💕 A gentle reminder</strong><br/>Your health journey is personal. There is no need to have everything figured out today. Use HerHealth AI to stay organized and prepare questions for a qualified healthcare professional.</div>',unsafe_allow_html=True)

with tabs[1]:
    st.image("https://images.unsplash.com/photo-1491013516836-7db643ee125a?auto=format&fit=crop&w=1400&q=80", caption="Every pregnancy journey is unique", use_container_width=True)
    st.title(t["preg_title"]); st.write(t["preg_desc"])
    lmp=st.date_input(t["lmp"],value=None,min_value=date(1900,1,1),max_value=date.today(),key="lmp")
    if lmp:
        days=(date.today()-lmp).days
        if days>=0:
            weeks,rem=divmod(days,7); due=lmp+timedelta(days=280)
            st.subheader(t["estimate"])
            a,b,c=st.columns(3)
            a.metric(t["weeks"],f"{weeks}w {rem}d")
            b.metric(t["due"],due.strftime("%d %b %Y"))
            c.metric(t["days"],str(days))
            st.caption(t["lmp_note"])
    st.divider()
    st.subheader(t["appointments"]); st.caption(t["appointment_help"])
    with st.form("visit_form",clear_on_submit=True):
        vd=st.date_input(t["appointment_date"],value=date.today(),key="vd")
        vt=st.selectbox(t["appointment_type"],t["preg_types"])
        vn=st.text_input(t["notes"])
        add=st.form_submit_button(t["add"])
        if add:
            st.session_state.visits.append({"Date":vd.isoformat(),"Type":vt,"Notes":vn,"Completed":False})
            st.success(t["saved"])
    if st.session_state.visits:
        vdf=pd.DataFrame(st.session_state.visits)
        edited=st.data_editor(vdf,use_container_width=True,hide_index=True,num_rows="dynamic",key="visit_editor")
        st.session_state.visits=edited.to_dict("records")
        st.download_button(t["download"],edited.to_csv(index=False),"herhealth_appointments.csv","text/csv", key="download_csv_1")
    else: st.caption(t["no_appointments"])

with tabs[2]:
    st.image("https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=1400&q=80", caption="Care that starts with understanding your body", use_container_width=True)
    st.title(t["pcos_title"]); st.write(t["pcos_desc"])
    st.info(t["pcos_info"])
    with st.form("cycle_form",clear_on_submit=True):
        ld=st.date_input(t["cycle_date"],value=date.today(),key="ld")
        cyc=st.selectbox(t["cycle_note"],t["cycle_types"])
        syms=st.multiselect(t["symptoms"],t["symptom_types"])
        ln=st.text_area(t["notes"])
        save=st.form_submit_button(t["save"])
        if save:
            st.session_state.logs.append({"Date":ld.isoformat(),"Cycle note":cyc,"Symptoms":", ".join(syms),"Notes":ln})
            st.success(t["journal_saved"])
    if st.session_state.logs:
        ldf=pd.DataFrame(st.session_state.logs)
        st.dataframe(ldf,use_container_width=True,hide_index=True)
        st.download_button(t["download"],ldf.to_csv(index=False),"herhealth_pcos_journal.csv","text/csv", key="download_csv_2")
    else: st.caption(t["no_entries"])
    with st.expander(t["wellbeing"]):
        st.markdown(t["wellbeing_text"])

with tabs[3]:
    st.title(t["ai_title"]); st.write(t["ai_desc"])
    q=st.text_area(t["question"],placeholder="Example: What does insulin resistance mean in PCOS?",height=120)
    if st.button(t["ask"],type="primary"):
        if not q.strip(): st.warning(t["ai_empty"])
        elif not api_key: st.warning(t["api_missing"])
        else:
            sys_prompt=f"""You are HerHealth AI, a cautious women's-health education assistant. Respond in {lang}. Give general educational information in plain language. Do not diagnose, determine whether the user has PCOS or another condition, prescribe or recommend medicines/supplements, provide individualized treatment, or replace a qualified clinician. For pregnancy, explain that checkup schedules and tests depend on local guidance and individual circumstances. LMP date calculations are estimates only. For PCOS, explain that symptoms overlap with other conditions and diagnosis requires clinician assessment. Do not infer diagnoses from symptoms. Encourage professional advice for personal concerns. For urgent or severe symptoms, advise contacting local emergency services or an appropriate healthcare professional promptly. Do not request identifying information. State uncertainty clearly."""
            try:
                client=genai.Client(api_key=api_key)
                with st.spinner("HerHealth AI is preparing an educational response..."):
                    resp=client.models.generate_content(
                        model=model,
                        contents=q,
                        config=types.GenerateContentConfig(
                            system_instruction=sys_prompt,
                            temperature=0.2,
                            max_output_tokens=900,
                        ),
                    )
                answer = (resp.text or "").strip()
                if not answer:
                    st.warning("The AI provider returned an empty response. Please try again.")
                else:
                    st.subheader(t["answer"]); st.write(answer); st.caption(t["ai_note"])
            except Exception as e: st.error(f"AI request failed: {e}")

with tabs[4]:
    st.title(t["planner_title"]); st.write(t["planner_desc"])
    if st.session_state.visits:
        st.subheader(t["appointments"])
        vdf=pd.DataFrame(st.session_state.visits)
        st.dataframe(vdf,use_container_width=True,hide_index=True)
        st.download_button(t["download"],vdf.to_csv(index=False),"herhealth_appointments.csv","text/csv", key="download_csv_3")
    if st.session_state.logs:
        st.subheader(t["journal"])
        ldf=pd.DataFrame(st.session_state.logs)
        st.dataframe(ldf,use_container_width=True,hide_index=True)
        st.download_button(t["download"],ldf.to_csv(index=False),"herhealth_pcos_journal.csv","text/csv", key="download_csv_4")
    if not st.session_state.visits and not st.session_state.logs: st.caption(t["no_entries"])

with tabs[5]:
    st.title(t["resources_title"])
    st.markdown("""
- [WHO – Promoting healthy pregnancy](https://www.who.int/activities/promoting-healthy-pregnancy)
- [WHO – Antenatal care recommendations](https://www.who.int/publications/i/item/9789241549912)
- [NHS – Antenatal care and appointments](https://www.nhs.uk/pregnancy/your-pregnancy-care/your-antenatal-care-and-appointments/)
- [Monash University – International PCOS guideline](https://www.monash.edu/medicine/mchri/pcos/guideline)
- [RCOG – International evidence-based PCOS guideline](https://www.rcog.org.uk/guidance/browse-all-guidance/other-guidelines-and-reports/international-evidence-based-guideline-on-polycystic-ovary-syndrome/)
- [India – Ministry of Health & Family Welfare](https://mohfw.gov.in/)
""")
    st.caption(t["resource_note"])

st.divider()
st.caption(t["footer"])

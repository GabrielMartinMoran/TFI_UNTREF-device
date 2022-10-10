// Creditos: https://www.youtube.com/watch?v=hArTsILiBR8

/*
Blog: www.descargatuscosas.blogspot.com
facebook: www.fb.com/LosMejoresContenidosParaTi
Instagram: www.instagram.com/marioalot
YouTube:www.youtube.com/user/descargatuscosas
*/

float Sensibilidad = 0.066; //sensibilidad en V/A para nuestro sensor
/*
 5A - 185mV/A - 0.185 v/A
 20A - 100mV/A - 0.100 v/A
 30A - 66mV/A - 0.066 v/A

 v = Im + 2.5 //m : sensibilidad
 Despejando la ecuación
 I = (v - 2.5)/m
*/
float iRef = 0.0;

void setup() {
  Serial.begin(115200);
  delay(1000); // Esperamos 1 segundo para evitar ruidos
  iRef = obtener_corriente(2); // Sensamos la corriente de ruido por 2 segundos
  Serial.print("Corriente de referencia (ruido): "); Serial.println(iRef,3);
}

void loop() {
  float Ip = obtener_corriente(1) - iRef; //obtenemos la corriente pico
  if (Ip < 0) Ip = 0;
  float Irms = Ip * 0.707; //Intensidad RMS = Ipico/(2^1/2)
  float P = Irms * 220.0; // P = I * V watts
  Serial.print("Ip: ");  Serial.print(Ip,3); Serial.print("A  ");
  Serial.print("Irms: "); Serial.print(Irms,3);Serial.print("A  ");
  Serial.print("Potencia: "); Serial.print(P,3); Serial.println("W");
  delay(500);
}

float obtener_corriente(int segundosMuestreo){
  float voltajeSensor;
  float corriente = 0;
  long tiempo = millis();
  float Imax=0;
  float Imin=0;
  while(millis() - tiempo<segundosMuestreo*1000){
    voltajeSensor = analogRead(34) * (3.3 / 4096.0);//lectura
    voltajeSensor -= 2.35; // 0A en sensor en 0 corresponde a 2.5V de salida -> El 2.35 se obtiene al medir la salida del sensor a 0A (valor de referencia 2.5V)
    corriente = 0.9*corriente+0.1*(voltajeSensor/Sensibilidad); //Ecuación  para obtener la corriente
    //corriente = voltajeSensor/Sensibilidad; //Ecuación  para obtener la corriente
    /*
    // Forzamos el valor absoluto
    if (corriente < 0){
      corriente *= -1;
    }
    */
    if(corriente>Imax){
      Imax = corriente;
    }
    if(corriente<Imin){
      Imin = corriente;
    }
  }
  return(((Imax-Imin)/2.0));
}
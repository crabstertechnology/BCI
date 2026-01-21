
# 📊 RESULTS AND DISCUSSION

---

## 1. Overview of Experiments Conducted

The developed system was evaluated through a series of controlled experiments to validate each stage of the EEG processing pipeline. The experiments were conducted on a single user using a BioAmp EXG Pill–based EEG acquisition setup and Arduino UNO R4 Minima for data digitization. The focus of evaluation was to verify signal validity, frequency-domain characteristics, and the effectiveness of the proposed calmness index in real-time biofeedback.

The evaluation was strictly **non-medical** and aimed at demonstrating feasibility for meditation training applications.

---

## 2. Raw EEG Signal Validation Results

### 2.1 Baseline Stability Test

A 60-second baseline EEG recording was performed under eyes-open resting conditions. The recorded signal showed continuous low-amplitude fluctuations without saturation or signal loss.

**Observation:**

* Signal was stable when the subject remained still
* No clipping at ADC limits
* Standard deviation remained within expected range for BioAmp-based EEG

**Inference:**
This confirmed correct electrode placement, grounding, and reliable signal acquisition.

---

### 2.2 Eye Blink Artifact Detection

During the eye blink test, intentional eye blinks produced large, sharp amplitude spikes in the EEG signal.

**Observation:**

* Blink artifacts were significantly larger than baseline fluctuations
* Spikes occurred synchronously with voluntary blinks

**Inference:**
The presence of strong eye blink artifacts confirmed that frontal EEG activity was being successfully captured.

---

### 2.3 Eyes Open vs Eyes Closed Test

A comparative time-domain analysis was performed between eyes-open and eyes-closed conditions.

**Observation:**

* Eyes-closed signal exhibited more rhythmic patterns
* Slight increase in signal amplitude compared to eyes-open condition

**Inference:**
This behavior is consistent with known EEG physiology and indicated readiness for frequency-domain analysis.

---

## 3. Signal Processing Results

### 3.1 Filtering Performance

The raw EEG signal was processed using:

* A 0.5–40 Hz band-pass filter
* A 50 Hz notch filter to remove power-line interference

**Results:**

* Low-frequency drift and high-frequency noise were significantly reduced
* The 50 Hz component was visibly attenuated in the power spectral density (PSD)

**Inference:**
The filtering stage produced a clean EEG signal suitable for feature extraction without distorting physiological information.

---

## 4. Frequency-Domain Analysis Results

### 4.1 FFT and Power Spectral Density

Welch’s method was used to estimate the power spectral density of the filtered EEG signal.

**Observation:**

* EEG power was concentrated below 30–40 Hz
* Distinct energy was observed in the Alpha (8–13 Hz) and Beta (13–30 Hz) bands

**Inference:**
The frequency-domain characteristics matched expected EEG band distributions.

---

### 4.2 Alpha and Beta Band Power Comparison

A quantitative comparison of Alpha and Beta band power was performed for eyes-open and eyes-closed conditions.

**Results:**

* Alpha power increased during eyes-closed condition
* Beta power was relatively higher during eyes-open condition
* Alpha/Beta ratio was consistently higher when eyes were closed

**Inference:**
This result validated the physiological basis for using the Alpha/Beta ratio as a relaxation-related metric.

---

## 5. Calmness Index Results (Deterministic Model)

### 5.1 Calmness Index Definition

The Calmness Index (CI) was defined as:

[
CI = \frac{\text{Alpha Power}}{\text{Beta Power}}
]

A user-specific baseline was established using relaxed eyes-closed data.

---

### 5.2 Threshold-Based Classification

Using baseline mean and standard deviation, calmness states were categorized into:

* Calm
* Neutral
* Not Calm

**Results:**

* Calmness Index increased during relaxed breathing
* Calmness Index decreased during distraction or movement
* State transitions were intuitive and consistent with user behavior

**Inference:**
The deterministic calmness model functioned reliably without requiring machine learning.

---

## 6. Real-Time Biofeedback Performance

The Calmness Index was computed in real time using sliding windows, and continuous feedback was provided to the user.

**Observations:**

* Stable calmness levels during sustained relaxation
* Immediate drop in calmness during movement or cognitive distraction
* Gradual improvement in calmness stability across sessions

**Inference:**
The system successfully acted as a real-time meditation biofeedback tool.

---

## 7. Discussion

The results demonstrate that meaningful EEG-based biofeedback can be achieved using classical signal processing and deterministic logic. The step-by-step validation ensured that each module contributed reliably to the final system.

Importantly, the system does not attempt emotion detection, diagnosis, or mind-reading. Instead, it focuses on **relative, personalized feedback**, which is appropriate for non-medical meditation training applications.

The deterministic Calmness Index provided interpretable results and formed a strong foundation for potential future AI-based enhancements.

---

## 8. Limitations

* Single-user evaluation
* Sensitive to motion and electrode placement
* Analog front-end introduces noise compared to medical-grade EEG systems
* Calmness Index is relative and not an absolute physiological measure

These limitations were acknowledged and intentionally accepted to maintain system simplicity and transparency.

---

## 9. Conclusion of Results

The experimental results confirm that the proposed system can reliably acquire EEG signals, extract frequency-domain features, and provide real-time personalized meditation feedback. The deterministic approach ensures interpretability and robustness, making the system suitable for educational and non-medical applications.

---

## 🔒 Examiner-Safe Closing Line (USE THIS)

> “The results validate that the proposed EEG-based meditation trainer provides consistent, physiologically meaningful biofeedback using classical signal processing, without relying on medical claims or opaque machine learning models.”


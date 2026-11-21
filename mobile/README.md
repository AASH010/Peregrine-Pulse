# mobile/

Thin native Android app (Kotlin). **No Gradle project exists yet** — it is created in task MOB-01 with Android Studio so that tool and plugin versions are pinned on a real setup. This folder currently documents the intended structure.

## Modules
- **`:core`** — pure Kotlin, no Android dependency: incident model, risk rules, capability inference, connectivity ladder, offline queue, state machine. Tested with plain JVM tests and replayed sensor traces.
- **`:android`** — implements the interfaces below with Android APIs and holds the screens.

```kotlin
// Interface sketch (not compiled yet)
interface Transport {
    suspend fun probe(): Reachability                       // real end-to-end reachability
    suspend fun send(payload: ByteArray, deadlineMs: Long): SendResult
}
interface SensorSource   { fun samples(): Flow<SensorSample> }
interface PushProvider   { /* FCM or HMS */ }
interface LocationProvider { suspend fun current(): LocationFix? }
interface Clock          { fun nowMs(): Long }
interface Storage        { /* encrypted local persistence, offline queue */ }
```

## Screens (six)
Onboarding + Consent · Registered Contacts · Home/Status · Verification (large "I'm OK" / "I need help" buttons) · Incident Timeline (evidence-backed stages only) · Simulator Panel (development and demo builds).

## Delivery slices
1. **Slice 1:** replay-driven app, no real background sensing.
2. **Slice 2:** real sensors in a foreground service on a listed device set.
3. **Slice 3:** hardening, HMS support, optional ESP32 channel.

Push and location go through an abstraction (FCM and HMS). No device compatibility is claimed without a test on a physical device. Related plan concepts: C06, C08, C16.

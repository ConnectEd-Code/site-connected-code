import urllib.request
import os

BASE = "/Users/reneenoble/Documents/ConnectEd Code/site-connected-code/docs"
SQ = "https://images.squarespace-cdn.com/content/v1/5f901a327c75ed4db2d1b617"

downloads = [
    # CubeSat Project 1 (8 images)
    (f"{SQ}/a19779d9-e161-495d-ba6a-8921bd394882/1.JPG?format=750w", f"{BASE}/cubesat/images/p1-step1.jpg"),
    (f"{SQ}/b0997a2f-7a1c-4829-a8ef-0d621125d302/2.JPG?format=750w", f"{BASE}/cubesat/images/p1-step2.jpg"),
    (f"{SQ}/840e4407-59d2-4783-a1d3-d08506941b94/3.JPG?format=750w", f"{BASE}/cubesat/images/p1-step3.jpg"),
    (f"{SQ}/73c73f7c-5b0d-496e-a653-cd49622925ba/4.JPG?format=750w", f"{BASE}/cubesat/images/p1-step4.jpg"),
    (f"{SQ}/a9972644-1a25-4ca0-966b-8e02591424a0/5.JPG?format=750w", f"{BASE}/cubesat/images/p1-step5.jpg"),
    (f"{SQ}/2eb034de-70fd-4fee-962a-4eb80ffe065e/6.JPG?format=750w", f"{BASE}/cubesat/images/p1-step6.jpg"),
    (f"{SQ}/7ce4f5d7-70b6-4a23-b63c-0df56d2172bd/7.JPG?format=750w", f"{BASE}/cubesat/images/p1-step7.jpg"),
    (f"{SQ}/9918202e-0fe8-43d9-96cb-a87bae31e8fe/8.JPG?format=750w", f"{BASE}/cubesat/images/p1-step8.jpg"),
    # CubeSat Project 2 (8 images)
    (f"{SQ}/7cb2c3e6-a397-4ef6-a77f-ed0e289a37db/1.JPG?format=750w", f"{BASE}/cubesat/images/p2-step1.jpg"),
    (f"{SQ}/4c0b6924-2e0a-4120-b638-1bb4b40cd3ba/2.JPG?format=750w", f"{BASE}/cubesat/images/p2-step2.jpg"),
    (f"{SQ}/50bd28e5-6b3a-41c7-a788-797382fde168/3.JPG?format=750w", f"{BASE}/cubesat/images/p2-step3.jpg"),
    (f"{SQ}/34dc915d-e985-4a22-82c4-a75f332bf571/4.JPG?format=750w", f"{BASE}/cubesat/images/p2-step4.jpg"),
    (f"{SQ}/b067f4a7-6893-4bd0-94b7-095f7fc19956/5.JPG?format=750w", f"{BASE}/cubesat/images/p2-step5.jpg"),
    (f"{SQ}/42efaf44-40ce-4886-a3b1-6c72a09ac383/6.JPG?format=750w", f"{BASE}/cubesat/images/p2-step6.jpg"),
    (f"{SQ}/a7f23090-e050-445f-896c-ba204317859e/7.JPG?format=750w", f"{BASE}/cubesat/images/p2-step7.jpg"),
    (f"{SQ}/afcbb459-576a-4c6e-a00a-26637632a19b/8.JPG?format=750w", f"{BASE}/cubesat/images/p2-step8.jpg"),
    # Playdough Xylophone (7 images)
    (f"{SQ}/aa1264f5-7f5a-43ae-b12f-fd2ee0280f49/PXL_20230704_095137109.jpg?format=750w", f"{BASE}/detechtives/images/xylophone-step1.jpg"),
    (f"{SQ}/30256227-bddf-405d-8d04-cfc00b4e1aed/PXL_20230704_095309479.jpg?format=750w", f"{BASE}/detechtives/images/xylophone-step2.jpg"),
    (f"{SQ}/12d566a4-95e4-4a1b-a64b-74e9b27bf8b2/PXL_20230704_095457699.jpg?format=750w", f"{BASE}/detechtives/images/xylophone-step3.jpg"),
    (f"{SQ}/b2b538dc-0131-4df0-87e2-a7f79e44b917/PXL_20230704_095543002.jpg?format=750w", f"{BASE}/detechtives/images/xylophone-step4.jpg"),
    (f"{SQ}/27587d0c-25b3-47e5-81fa-9453839c2464/PXL_20230704_095545107.jpg?format=750w", f"{BASE}/detechtives/images/xylophone-step5.jpg"),
    (f"{SQ}/b5cae3c7-6cee-4f3b-b5e7-50be8e9b4cc5/PXL_20230704_095713311.jpg?format=750w", f"{BASE}/detechtives/images/xylophone-step6.jpg"),
    (f"{SQ}/f88c2f60-2f54-4dee-9c82-eab2d7e70de3/PXL_20230704_095941540.jpg?format=750w", f"{BASE}/detechtives/images/xylophone-step7.jpg"),
    # Lockdown Learning Support (5 images)
    (f"{SQ}/1629104053781-7KM2PPD9KKO4GOCHAB3K/image-asset.jpeg?format=750w", f"{BASE}/events/images/lockdown-1.jpg"),
    (f"{SQ}/1629104113344-WKHJL0HJZFZ7IAQRXR9B/image-asset.jpeg?format=750w", f"{BASE}/events/images/lockdown-2.jpg"),
    (f"{SQ}/1629104162145-BPKTG30WCLMEI0G63EWP/39991385_10217172241116813_8677258879219793920_n.jpg?format=750w", f"{BASE}/events/images/lockdown-3.jpg"),
    (f"{SQ}/1629105221532-GHVLWMNMHLV8TSCVMITD/Frame+2+%281%29.png?format=750w", f"{BASE}/events/images/lockdown-how-it-works.png"),
    (f"{SQ}/1629105285404-JZ39F9XATIG3IEPYX5FM/image-asset.jpeg?format=750w", f"{BASE}/events/images/lockdown-5.jpg"),
    # School Events / Incursions shared image
    (f"{SQ}/8921299d-9b51-4ae7-8af1-a20e49305df4/PXL_20220517_012350852+%281%29.jpg?format=750w", f"{BASE}/events/images/school-incursion.jpg"),
    # Tutors shared images
    (f"{SQ}/1650353369123-5VJHRVHG6CB33OL7HUQ6/unsplash-image-cS2eQHB7wE4.jpg?format=750w", f"{BASE}/tutors/images/tutor-coding.jpg"),
    (f"{SQ}/1650353505700-SNYP3UT6K6DWR0WUIW5E/unsplash-image-OmaFZNYOy6E.jpg?format=750w", f"{BASE}/tutors/images/tutor-teaching.jpg"),
    (f"{SQ}/53bb7e4b-c68b-4b64-be1e-4f9fea5e6e8e/PXL_20220411_073148963.jpg?format=750w", f"{BASE}/tutors/images/kookaberry-event.jpg"),
    # Team page - Jack's photo
    (f"{SQ}/867fb69c-2506-4f06-98f5-18f6eaef19e5/PXL_20230701_092023287.PORTRAIT.jpg?format=500w", f"{BASE}/images/jack.jpg"),
    # Free Resources images
    (f"{SQ}/1632207100380-RZPMMBWBTK23QZYJVUON/image-asset.png?format=750w", f"{BASE}/images/python-cheatsheet.png"),
    (f"{SQ}/3defb85c-82c3-4d41-bb7b-7a8c3b9e0dfa/jessica-ruscello-OQSCtabGkSY-unsplash+%281%29.jpg?format=750w", f"{BASE}/images/free-resources-hero.jpg"),
    # KookaSuite index images
    (f"{SQ}/2c8f0a35-1e6a-4e0b-90da-0d4f8e8cd13a/Frame+Colour%3DGreen%2C+Lettered%3DOn.png?format=500w", f"{BASE}/kookasuite/images/kookaberry-device.png"),
    (f"{SQ}/7cbf1ef1-70b3-4aca-82e5-d4f4bf6e91f2/Screen+Shot+2022-05-01+at+6.48.08+pm.png?format=750w", f"{BASE}/kookasuite/images/kookasuite-screenshot.png"),
]

total = len(downloads)
ok = 0
fail = 0
for i, (url, dest) in enumerate(downloads, 1):
    if os.path.exists(dest) and os.path.getsize(dest) > 100:
        print(f"[{i}/{total}] SKIP: {os.path.basename(dest)}")
        ok += 1
        continue
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r, open(dest, 'wb') as f:
            f.write(r.read())
        sz = os.path.getsize(dest)
        print(f"[{i}/{total}] OK ({sz//1024}KB): {os.path.basename(dest)}")
        ok += 1
    except Exception as e:
        print(f"[{i}/{total}] FAIL: {os.path.basename(dest)} - {e}")
        fail += 1

print(f"\nDone! {ok} OK, {fail} failed")

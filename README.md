+-------------+                      +--------------------+
|             |  Generates traffic   |                    |
|  Generator  +--------------------->+   Discriminator    |
|(Attacker AI)|                      | (Anomaly Detector) |
|             |<---------------------+                    |
+-------------+    Feedback loop     +---------+----------+
                                               |
                                               |
                                      Anomaly Detection Result
                                               |
                                  +------------v------------+
                                  | OpenAI GPT Verification |
                                  +-------------------------+

# class HolisticCommandRecognition():
#     def _execute(self) -> tuple:
#         command = Command.NONE, None
#
#         r_hand = self._get_hands_info(hand_no="rx")
#         if r_hand:
#             # (cx, cy) = r_hand["center"]
#             (wx, wy, wz) = r_hand["lmList"][Hand.Keypoints.WRIST.value]
#             (pmx, pmy, pmz) = r_hand["lmList"][Hand.Keypoints.PINKY_MCP.value]
#             (imx, imy, imz) = r_hand["lmList"][Hand.Keypoints.INDEX_FINGER_MCP.value]
#             (itx, ity, itz) = r_hand["lmList"][Hand.Keypoints.INDEX_FINGER_TIP.value]
#
#             minDist = max(math.dist((wx, wy), (pmx, pmy)), math.dist((imx, imy), (pmx, pmy)))*0.75
#
#             distance = math.dist((imx, imy), (itx, ity))
#             angle = math.degrees(math.atan2(ity-imy, itx-imx))
#             #print(angle)
#             delta = 25  # max 45
#
#             (mtx, mty, mtz) = r_hand["lmList"][Hand.Keypoints.MIDDLE_FINGER_TIP.value]
#             (rtx, rty, rtz) = r_hand["lmList"][Hand.Keypoints.RING_FINGER_TIP.value]
#             (ptx, pty, ptz) = r_hand["lmList"][Hand.Keypoints.PINKY_TIP.value]
#             (rmx, rmy, rmz) = r_hand["lmList"][Hand.Keypoints.RING_FINGER_MCP.value]
#
#             otherFingersDist = max(math.dist((mtx, mty), (rmx, rmy)),
#                                    math.dist((rtx, rty), (rmx, rmy)),
#                                    math.dist((ptx, pty), (rmx, rmy)))
#             if otherFingersDist > minDist:
#                 return Command.NONE, None
#
#             if distance > minDist:
#                 if (-45 + delta) < angle < (45 - delta):
#                     command = Command.ROTATE_CW, 15 # Blue -> left
#                 elif (45 + delta) < angle < (135 - delta):
#                     command = Command.LAND, None # Green -> bottom
#                 elif (-135 + delta) < angle < (-45 - delta):
#                     command = Command.TAKE_OFF, None # Red -> top
#                 elif (135+delta) < angle or angle < (-135-delta):
#                     command = Command.ROTATE_CCW, 15 # magenta -> right
#
#         return command
#
#     def edit_frame(self, frame):
#         for hand in self.all_hands:
#             bbox = hand["bbox"]
#             cv2.rectangle(frame, (bbox[0] - 20, bbox[1] - 20),
#                           (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
#                           (255, 0, 255), 2)
#             cv2.putText(frame, hand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
#                         2, (0, 0, 255), 2)
#
#         r_hand = self._get_hands_info(hand_no="rx")
#         if r_hand:
#             (wx, wy, wz) = r_hand["lmList"][Hand.Keypoints.WRIST.value]
#             (pmx, pmy, pmz) = r_hand["lmList"][Hand.Keypoints.PINKY_MCP.value]
#             (imx, imy, imz) = r_hand["lmList"][Hand.Keypoints.INDEX_FINGER_MCP.value]
#             (itx, ity, itz) = r_hand["lmList"][Hand.Keypoints.INDEX_FINGER_TIP.value]
#
#             minDist = max(math.dist((wx, wy), (pmx, pmy)), math.dist((imx, imy), (pmx, pmy)))*0.75
#
#             distance = math.dist((imx, imy), (itx, ity))
#             angle = math.degrees(math.atan2(ity-imy, itx-imx))
#             #print(angle)
#             draw_command_color = (0, 0, 0)
#             delta = 25  # max 45
#             action = ""
#
#             (mtx, mty, mtz) = r_hand["lmList"][Hand.Keypoints.MIDDLE_FINGER_TIP.value]
#             (rtx, rty, rtz) = r_hand["lmList"][Hand.Keypoints.RING_FINGER_TIP.value]
#             (ptx, pty, ptz) = r_hand["lmList"][Hand.Keypoints.PINKY_TIP.value]
#             (rmx, rmy, rmz) = r_hand["lmList"][Hand.Keypoints.RING_FINGER_MCP.value]
#
#             otherFingersDist = max(math.dist((mtx, mty), (rmx, rmy)),
#                                    math.dist((rtx, rty), (rmx, rmy)),
#                                    math.dist((ptx, pty), (rmx, rmy)))
#             if otherFingersDist > minDist:
#                 return frame
#
#             if distance > minDist:
#                 if (-45 + delta) < angle < (45 - delta):
#                     draw_command_color = (255, 0, 0) # Blue -> left
#                     action = "ROTATE_CW"
#                 elif (45 + delta) < angle < (135 - delta):
#                     draw_command_color = (0, 255, 0) # Green -> bottom
#                     action = "LAND"
#                 elif (-135 + delta) < angle < (-45 - delta):
#                     draw_command_color = (0, 0, 255) # Red -> top
#                     action = "MOVE_FORWARD"
#                 elif (135+delta) < angle or angle < (-135-delta):
#                     draw_command_color = (255, 0, 255) # magenta -> right
#                     action = "ROTATE_CCW"
#
#             cv2.line(frame, (imx, imy), (itx, ity), draw_command_color, 2)
#             cv2.putText(frame, action, (itx, ity), cv2.FONT_HERSHEY_PLAIN, 2, draw_command_color, 2)
#
#         return frame
#
#     def _get_hands_info(self, hand_no):
#         if isinstance(hand_no, int):
#             if hand_no < 0:
#                 return self.all_hands
#             else:
#                 if hand_no <= len(self.all_hands):
#                     return self.all_hands[hand_no]
#         elif isinstance(hand_no, str):
#             if hand_no.lower() == "lx":
#                 for hand in self.all_hands:
#                     if hand["type"].lower() == "lx":
#                         return hand
#             elif hand_no.lower() == "rx":
#                 for hand in self.all_hands:
#                     if hand["type"].lower() == "rx":
#                         return hand
#         return []
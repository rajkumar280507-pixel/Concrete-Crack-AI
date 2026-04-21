import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiService {
  // Connected to live Render Cloud Backend for Global Access
  static const String baseUrl = 'https://concrete-crack-ai.onrender.com';

  static Future<Map<String, dynamic>> uploadImage(File imageFile) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/predict'));
      request.files.add(await http.MultipartFile.fromPath('file', imageFile.path));
      
      var response = await request.send();
      var responseData = await response.stream.bytesToString();
      
      if (response.statusCode == 200) {
        return json.decode(responseData);
      } else {
        return {"status": "error", "message": "Server Error: ${response.statusCode}"};
      }
    } catch (e) {
      return {"status": "error", "message": "Connection Failed: Check your internet or server IP."};
    }
  }

  static Future<List<dynamic>> getHistory() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/get_history'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['history'] ?? [];
      }
      return [];
    } catch (e) {
      return [];
    }
  }
}

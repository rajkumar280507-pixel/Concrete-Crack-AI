import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';

class ResultScreen extends StatelessWidget {
  final Map<String, dynamic> data;

  const ResultScreen({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    bool hasCrack = data['crack_detected'] ?? false;
    bool isValidConcrete = data['is_valid_concrete'] ?? false;

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: Text("Analysis Result", style: GoogleFonts.outfit()),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildImageDisplay(),
            const SizedBox(height: 24),
            _buildStatusBadge(hasCrack, isValidConcrete),
            const SizedBox(height: 16),
            Text(
              data['message'] ?? "",
              style: GoogleFonts.outfit(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w500),
            ),
            const Divider(color: Colors.white10, height: 40),
            
            if (hasCrack) ...[
              _buildMetricTile("Severity", data['severity'], Icons.warning_amber, Colors.orange),
              _buildMetricTile("Hazard", data['hazard'], Icons.gpp_maybe, Colors.redAccent),
              _buildMetricTile("Crack Type", data['crack_type'] ?? "Structural", Icons.category, Colors.blue),
              const SizedBox(height: 20),
              _buildDimensionsCard(data['measurements']),
              const SizedBox(height: 20),
              _buildRecommendationCard(data['recommendation']),
            ] else ...[
              _buildSafetyGuidelines(),
            ]
          ],
        ),
      ),
    );
  }

  Widget _buildImageDisplay() {
    return Container(
      height: 250,
      width: double.infinity,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white10),
      ),
      clipBehavior: Clip.antiAlias,
      child: Image.network(
        "${ApiService.baseUrl}${data['processed_url']}",
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) => const Icon(Icons.broken_image, size: 50, color: Colors.white24),
      ),
    );
  }

  Widget _buildStatusBadge(bool hasCrack, bool isValid) {
    Color color = hasCrack ? Colors.redAccent : (isValid ? Colors.greenAccent : Colors.orangeAccent);
    String label = hasCrack ? "CRACK DETECTED" : (isValid ? "NO CRACK DETECTED" : "INVALID SURFACE");
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: color.withOpacity(0.5)),
      ),
      child: Text(
        label,
        style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 12),
      ),
    );
  }

  Widget _buildMetricTile(String title, dynamic value, IconData icon, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Icon(icon, color: color),
        title: Text(title, style: const TextStyle(color: Colors.white70, fontSize: 14)),
        trailing: Text(
          value.toString(),
          style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
        ),
        tileColor: Colors.white.withOpacity(0.05),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  Widget _buildDimensionsCard(Map<String, dynamic>? m) {
    if (m == null) return Container();
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.cyanAccent.withOpacity(0.05),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.cyanAccent.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("Measurements", style: TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _dimItem("Length", "${m['length_val']} ${m['unit']}"),
              _dimItem("Width", "${m['avg_width_val']} ${m['unit']}"),
              _dimItem("Depth", "${m['depth_val']} ${m['unit']}"),
            ],
          )
        ],
      ),
    );
  }

  Widget _dimItem(String label, String val) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.white54, fontSize: 12)),
        Text(val, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
      ],
    );
  }

  Widget _buildRecommendationCard(String? text) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("Professional Recommendation", style: TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          Text(text ?? "No recommendation available.", style: const TextStyle(color: Colors.white70)),
        ],
      ),
    );
  }

  Widget _buildSafetyGuidelines() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.orange.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: const Row(
        children: [
          Icon(Icons.tips_and_updates, color: Colors.orangeAccent),
          SizedBox(width: 12),
          Expanded(
            child: Text(
              "Ensure the surface is clean, well-lit concrete for accurate analysis.",
              style: TextStyle(color: Colors.white70),
            ),
          )
        ],
      ),
    );
  }
}

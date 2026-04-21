import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'package:intl/intl.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  late Future<List<dynamic>> _history;

  @override
  void initState() {
    super.initState();
    _history = ApiService.getHistory();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text("Scan History"),
        backgroundColor: Colors.transparent,
      ),
      body: FutureBuilder<List<dynamic>>(
        future: _history,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text("No records found", style: TextStyle(color: Colors.white38)));
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: snapshot.data!.length,
            itemBuilder: (context, index) {
              final item = snapshot.data![index];
              bool hasCrack = item['crack_detected'] == 1;
              
              return Card(
                color: Colors.white.withOpacity(0.05),
                margin: const EdgeInsets.only(bottom: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                child: ListTile(
                  leading: ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Image.network(
                      "${ApiService.baseUrl}/static/uploads/${item['original_img']}",
                      width: 50, height: 50, fit: BoxFit.cover,
                      errorBuilder: (c, e, s) => const Icon(Icons.image, color: Colors.white24),
                    ),
                  ),
                  title: Text(item['id'], style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  subtitle: Text(
                    DateFormat('dd MMM yyyy, hh:mm a').format(DateTime.parse(item['timestamp'])),
                    style: const TextStyle(color: Colors.white54, fontSize: 12),
                  ),
                  trailing: Icon(
                    hasCrack ? Icons.warning_rounded : Icons.check_circle_outline,
                    color: hasCrack ? Colors.redAccent : Colors.greenAccent,
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
